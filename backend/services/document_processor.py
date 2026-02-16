import re
from dataclasses import dataclass

import fitz  # PyMuPDF
from docx import Document as DocxDocument

from config import settings
from utils import count_tokens


@dataclass
class TextChunk:
    content: str
    page_number: int | None
    section: str | None
    token_count: int


def parse_pdf(file_path: str) -> list[dict]:
    """Parse PDF and return list of {text, page_number} per page."""
    doc = fitz.open(file_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():
            pages.append({"text": text, "page_number": page_num})
    doc.close()
    return pages


def parse_docx(file_path: str) -> list[dict]:
    """Parse DOCX and return list of {text, page_number} per paragraph group."""
    doc = DocxDocument(file_path)
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append({
                "text": text,
                "page_number": None,
                "style": para.style.name if para.style else None,
            })
    return paragraphs


def _detect_section_header(text: str) -> str | None:
    """Try to detect section headers like 'Section 1.2' or 'ARTICLE III'."""
    patterns = [
        r"^(Section\s+[\d.]+[^.\n]*)",
        r"^(ARTICLE\s+[IVXLCDM\d]+[^.\n]*)",
        r"^(\d+\.\d*\s+[A-Z][^\n]*)",
    ]
    for pattern in patterns:
        match = re.match(pattern, text.strip(), re.IGNORECASE)
        if match:
            return match.group(1).strip()[:200]
    return None


def chunk_text(pages: list[dict], target_tokens: int | None = None, overlap_tokens: int | None = None) -> list[TextChunk]:
    """Chunk parsed document text into segments with overlap."""
    target = target_tokens or settings.chunk_target_tokens
    overlap = overlap_tokens or settings.chunk_overlap_tokens

    # Combine all text with page markers
    segments: list[dict] = []
    for page in pages:
        text = page["text"]
        # Split into paragraphs
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n(?=[A-Z\d])", text) if p.strip()]
        for para in paragraphs:
            segments.append({
                "text": para,
                "page_number": page.get("page_number"),
                "tokens": count_tokens(para),
            })

    chunks: list[TextChunk] = []
    current_text = ""
    current_tokens = 0
    current_page = segments[0]["page_number"] if segments else None
    current_section = None

    for seg in segments:
        section = _detect_section_header(seg["text"])
        if section:
            current_section = section

        # If adding this segment would exceed target, finalize current chunk
        if current_tokens > 0 and current_tokens + seg["tokens"] > target:
            chunks.append(TextChunk(
                content=current_text.strip(),
                page_number=current_page,
                section=current_section,
                token_count=current_tokens,
            ))
            # Overlap: keep last portion of current text
            overlap_text = _get_overlap(current_text, overlap)
            current_text = overlap_text + "\n\n" + seg["text"]
            current_tokens = count_tokens(current_text)
            current_page = seg["page_number"] or current_page
        else:
            current_text += ("\n\n" if current_text else "") + seg["text"]
            current_tokens += seg["tokens"]
            current_page = seg["page_number"] or current_page

    # Final chunk
    if current_text.strip():
        chunks.append(TextChunk(
            content=current_text.strip(),
            page_number=current_page,
            section=current_section,
            token_count=count_tokens(current_text.strip()),
        ))

    return chunks


def _get_overlap(text: str, overlap_tokens: int) -> str:
    """Get the last ~overlap_tokens worth of text."""
    if overlap_tokens <= 0:
        return ""
    words = text.split()
    # Rough approximation: 1 token ≈ 0.75 words
    word_count = int(overlap_tokens * 0.75)
    if word_count <= 0 or word_count >= len(words):
        return text
    return " ".join(words[-word_count:])


def parse_and_chunk(file_path: str, file_type: str) -> list[TextChunk]:
    """Main entry point: parse a file and return chunks."""
    if file_type == "pdf":
        pages = parse_pdf(file_path)
    elif file_type == "docx":
        pages = parse_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    if not pages:
        return []

    return chunk_text(pages)
