import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models import Conversation, Message

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    citations: str | None
    created_at: str

    model_config = {"from_attributes": True}


class ConversationDetailResponse(BaseModel):
    id: str
    title: str
    messages: list[MessageResponse]


class CreateConversationRequest(BaseModel):
    title: str = "New Conversation"


class UpdateConversationRequest(BaseModel):
    title: str


@router.post("", response_model=ConversationResponse)
async def create_conversation(req: CreateConversationRequest, db: AsyncSession = Depends(get_db)):
    conv = Conversation(title=req.title)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return ConversationResponse(
        id=str(conv.id),
        title=conv.title,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        message_count=0,
    )


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversation).order_by(Conversation.updated_at.desc())
    )
    convs = result.scalars().all()
    responses = []
    for conv in convs:
        msg_result = await db.execute(
            select(Message.id).where(Message.conversation_id == conv.id)
        )
        msg_count = len(msg_result.all())
        responses.append(ConversationResponse(
            id=str(conv.id),
            title=conv.title,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat(),
            message_count=msg_count,
        ))
    return responses


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationDetailResponse(
        id=str(conv.id),
        title=conv.title,
        messages=[
            MessageResponse(
                id=str(msg.id),
                role=msg.role,
                content=msg.content,
                citations=msg.citations,
                created_at=msg.created_at.isoformat(),
            )
            for msg in conv.messages
        ],
    )


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(conversation_id: str, req: UpdateConversationRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.title = req.title
    await db.commit()
    await db.refresh(conv)
    msg_result = await db.execute(select(Message.id).where(Message.conversation_id == conv.id))
    return ConversationResponse(
        id=str(conv.id),
        title=conv.title,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        message_count=len(msg_result.all()),
    )


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conv)
    await db.commit()
    return {"status": "deleted"}
