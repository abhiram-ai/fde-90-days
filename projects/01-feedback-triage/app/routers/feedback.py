from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import Feedback, FeedbackSource


router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
    responses={404: {"description": "Not found"}},
)

class FeedbackCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="The feedback content cannot be empty")
    source: FeedbackSource
    customer_email: Optional[EmailStr] = None

class FeedbackResponse(FeedbackCreate):
    id: UUID
    created_at: datetime
    category: str = "uncategorized"
    priority: str = "medium"
    reviewed: bool = False

    model_config = {"from_attributes": True}

@router.post("/", response_model=FeedbackResponse, status_code=201)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    db_feedback = Feedback(
        text=feedback.text,
        source=feedback.source,
        customer_email=feedback.customer_email
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(feedback_id: UUID, db: Session = Depends(get_db)):
    db_feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_feedback

@router.get("/", response_model=List[FeedbackResponse])
def list_feedback(
    source: Optional[FeedbackSource] = Query(None, description="Filter by feedback source"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    query = db.query(Feedback)
    if source:
        query = query.filter(Feedback.source == source)
    return query.offset(skip).limit(limit).all()