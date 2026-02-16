import logging
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models import Document, DocumentChunk
from services.document_processor import parse_and_chunk
from services.embedding import generate_embeddings

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_TYPES = {"application/pdf": "pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx"}


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    page_count: int | None
    chunk_count: int
    created_at: str

    model_config = {"from_attributes": True}


@router.post("", response_model=DocumentResponse)
async def upload_document(file: UploadFile, db: AsyncSession = Depends(get_db)):
    # Validate file type
    content_type = file.content_type or ""
    file_type = ALLOWED_TYPES.get(content_type)
    if not file_type:
        # Fallback: check extension
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext == ".pdf":
            file_type = "pdf"
        elif ext == ".docx":
            file_type = "docx"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: PDF, DOCX")

    # Save file
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_id = uuid.uuid4()
    file_ext = "pdf" if file_type == "pdf" else "docx"
    file_path = os.path.join(settings.upload_dir, f"{file_id}.{file_ext}")

    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max: {settings.max_upload_size_mb}MB")

    with open(file_path, "wb") as f:
        f.write(content)

    # Parse and chunk
    try:
        chunks = parse_and_chunk(file_path, file_type)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=422, detail=f"Failed to parse document: {e}")

    if not chunks:
        os.remove(file_path)
        raise HTTPException(status_code=422, detail="No text content found in document")

    # Generate embeddings in batches
    try:
        batch_size = 100
        all_embeddings: list[list[float]] = []
        for i in range(0, len(chunks), batch_size):
            batch_texts = [c.content for c in chunks[i : i + batch_size]]
            batch_embeddings = await generate_embeddings(batch_texts)
            all_embeddings.extend(batch_embeddings)
    except Exception as e:
        os.remove(file_path)
        logger.exception("Embedding generation failed")
        raise HTTPException(status_code=502, detail=f"Embedding generation failed: {e}")

    # Compute page count
    page_numbers = [c.page_number for c in chunks if c.page_number is not None]
    page_count = max(page_numbers) if page_numbers else None

    # Store document
    doc = Document(
        id=file_id,
        filename=file.filename or "unknown",
        file_type=file_type,
        file_path=file_path,
        file_size=len(content),
        page_count=page_count,
    )
    db.add(doc)

    # Store chunks with embeddings
    for idx, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
        db_chunk = DocumentChunk(
            document_id=file_id,
            chunk_index=idx,
            content=chunk.content,
            page_number=chunk.page_number,
            section=chunk.section,
            token_count=chunk.token_count,
            embedding=embedding,
        )
        db.add(db_chunk)

    await db.commit()
    await db.refresh(doc)

    return DocumentResponse(
        id=str(doc.id),
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        page_count=doc.page_count,
        chunk_count=len(chunks),
        created_at=doc.created_at.isoformat(),
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    docs = result.scalars().all()
    responses = []
    for doc in docs:
        chunk_result = await db.execute(
            select(DocumentChunk.id).where(DocumentChunk.document_id == doc.id)
        )
        chunk_count = len(chunk_result.all())
        responses.append(DocumentResponse(
            id=str(doc.id),
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            page_count=doc.page_count,
            chunk_count=chunk_count,
            created_at=doc.created_at.isoformat(),
        ))
    return responses


class CreateFromTextRequest(BaseModel):
    content: str
    filename: str = "generated_document.pdf"


@router.post("/from-text", response_model=DocumentResponse)
async def create_document_from_text(req: CreateFromTextRequest, db: AsyncSession = Depends(get_db)):
    """Create a PDF document from text content (e.g., AI-generated drafts)."""
    import fitz  # PyMuPDF

    os.makedirs(settings.upload_dir, exist_ok=True)
    file_id = uuid.uuid4()
    file_path = os.path.join(settings.upload_dir, f"{file_id}.pdf")

    # Create PDF from text
    pdf_doc = fitz.open()
    # Split text into pages (~3000 chars per page to avoid overflow)
    text = req.content
    chars_per_page = 3000
    page_num = 0
    while text:
        page = pdf_doc.new_page(width=612, height=792)  # Letter size
        page_text = text[:chars_per_page]
        text = text[chars_per_page:]
        # Insert with margins
        rect = fitz.Rect(54, 54, 558, 738)
        page.insert_textbox(rect, page_text, fontsize=10, fontname="helv")
        page_num += 1
    pdf_doc.save(file_path)
    file_size = os.path.getsize(file_path)
    pdf_doc.close()

    # Parse and chunk the generated PDF
    try:
        chunks = parse_and_chunk(file_path, "pdf")
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=422, detail=f"Failed to process document: {e}")

    if not chunks:
        os.remove(file_path)
        raise HTTPException(status_code=422, detail="No text content generated")

    # Generate embeddings
    try:
        batch_texts = [c.content for c in chunks]
        all_embeddings = await generate_embeddings(batch_texts)
    except Exception as e:
        os.remove(file_path)
        logger.exception("Embedding generation failed")
        raise HTTPException(status_code=502, detail=f"Embedding generation failed: {e}")

    # Ensure filename ends with .pdf
    filename = req.filename if req.filename.endswith(".pdf") else req.filename + ".pdf"

    doc = Document(
        id=file_id,
        filename=filename,
        file_type="pdf",
        file_path=file_path,
        file_size=file_size,
        page_count=page_num,
    )
    db.add(doc)

    for idx, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
        db_chunk = DocumentChunk(
            document_id=file_id,
            chunk_index=idx,
            content=chunk.content,
            page_number=chunk.page_number,
            section=chunk.section,
            token_count=chunk.token_count,
            embedding=embedding,
        )
        db.add(db_chunk)

    await db.commit()
    await db.refresh(doc)

    return DocumentResponse(
        id=str(doc.id),
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        page_count=doc.page_count,
        chunk_count=len(chunks),
        created_at=doc.created_at.isoformat(),
    )


@router.get("/{document_id}/file")
async def get_document_file(document_id: str, db: AsyncSession = Depends(get_db)):
    """Serve the original uploaded file for preview."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    media_type = "application/pdf" if doc.file_type == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(
        doc.file_path,
        media_type=media_type,
        filename=doc.filename,
        headers={"Content-Disposition": f"inline; filename=\"{doc.filename}\""},
    )


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await db.delete(doc)
    await db.commit()
    return {"status": "deleted"}
