from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum
from typing import Dict, Optional, List



router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
    responses={404: {"description": "Not found"}},
)

class FeedbackSource(str, Enum):
    email = "email"
    slack = "slack"
    app = "app"
    other = "other"

class FeedbackCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, description="The feedback content cannot be empty")
    source: FeedbackSource
    customer_email: EmailStr

class FeedbackResponse(FeedbackCreate):
    id: UUID
    created_at: datetime
    category: str = "uncategorized"
    priority: str = "medium"

# In-memory storage (keyed by UUID)
feedback_db: Dict[UUID, FeedbackResponse] = {}

@router.post("/", response_model=FeedbackResponse, status_code=201)
def create_feedback(feedback: FeedbackCreate):
    feedback_id = uuid4()
    new_feedback = FeedbackResponse(
        id=feedback_id,
        created_at=datetime.now(timezone.utc),
        text=feedback.text,
        source=feedback.source,
        customer_email=feedback.customer_email
    )
    feedback_db[feedback_id] = new_feedback
    return new_feedback

@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(feedback_id: UUID):
    if feedback_id not in feedback_db:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback_db[feedback_id]

@router.get("/", response_model=List[FeedbackResponse])
def list_feedback(
    source: Optional[FeedbackSource] = Query(None, description="Filter by feedback source"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return")
):
    feedbacks = list(feedback_db.values())
    if source:
        feedbacks = [f for f in feedbacks if f.source == source]
        
    # Apply pagination via list slicing
    return feedbacks[skip : skip + limit]