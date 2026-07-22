import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Conversation, Message
from services.rag_service import query as rag_query
from schemas import (
    ChatNewResponse, ChatRequest, ChatResponse,
    ChatHistoryResponse, MessageItem, SourceItem,
)

router = APIRouter(prefix="/chat", tags=["对话"])


@router.post("/new", response_model=ChatNewResponse)
def new_conversation(db: Session = Depends(get_db)):
    """新建对话"""
    conv = Conversation(title="新对话")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ChatNewResponse(
        conversation_id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
    )


@router.post("/send", response_model=ChatResponse)
def send_message(
    body: ChatRequest,
    db: Session = Depends(get_db),
):
    """发送消息，获取 AI 回复"""
    # 验证会话存在
    conv = db.query(Conversation).filter(Conversation.id == body.conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")

    result = rag_query(body.message, body.conversation_id, db)

    # 转换 sources 为 SourceItem 列表
    source_items = [
        SourceItem(
            title=s.get("title", ""),
            content_snippet=s.get("content_snippet", ""),
            score=s.get("score"),
        )
        for s in result["sources"]
    ]

    return ChatResponse(
        conversation_id=result["conversation_id"],
        message_id=result["message_id"],
        answer=result["answer"],
        sources=source_items,
    )


@router.get("/history/{conversation_id}", response_model=ChatHistoryResponse)
def get_history(
    conversation_id: str,
    db: Session = Depends(get_db),
):
    """获取对话历史"""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="会话不存在")

    return ChatHistoryResponse(
        conversation_id=conv.id,
        title=conv.title,
        messages=[MessageItem.model_validate(msg) for msg in conv.messages],
    )
