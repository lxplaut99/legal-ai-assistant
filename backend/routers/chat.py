import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Conversation, Message
from services.citation import build_citations, format_context_for_llm
from services.llm import stream_chat_with_context
from services.retrieval import hybrid_search

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    conversation_id: str
    message: str
    document_ids: list[str] | None = None  # Filter to specific documents


@router.post("")
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    # Get or validate conversation
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == req.conversation_id)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=req.message,
    )
    db.add(user_msg)
    await db.flush()

    # Retrieve relevant chunks
    retrieved = await hybrid_search(req.message, db, limit=8, document_ids=req.document_ids)

    # Build citations and context
    citations = build_citations(retrieved)
    context = format_context_for_llm(citations)

    # Build conversation history for LLM
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in conversation.messages
    ]

    # Stream response via SSE
    has_documents = len(citations) > 0
    citations_json = json.dumps([c.to_dict() for c in citations])

    async def event_stream():
        full_response = ""
        async for chunk in stream_chat_with_context(req.message, context, history, has_documents=has_documents):
            full_response += chunk
            yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

        # Send citations
        yield f"data: {json.dumps({'type': 'citations', 'citations': [c.to_dict() for c in citations]})}\n\n"

        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=full_response,
            citations=citations_json,
        )
        db.add(assistant_msg)
        await db.commit()

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
