from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Feedback
from schemas import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["反馈"])


@router.post("/", response_model=FeedbackResponse)
def submit_feedback(
    body: FeedbackRequest,
    db: Session = Depends(get_db),
):
    """提交消息反馈（有帮助/无帮助）"""
    fb = Feedback(
        message_id=body.message_id,
        rating=body.rating,
        comment=body.comment,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)

    return FeedbackResponse(
        id=fb.id,
        message_id=fb.message_id,
        rating=fb.rating,
        comment=fb.comment,
        created_at=fb.created_at,
    )
