from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(
    title="Feedback API",
    description="A simple service to collect and categorize customer feedback"
)

class FeedbackSource(str, Enum):
    email = "email"
    slack = "slack"
    app = "app"
    other = "other"

class FeedbackCreate(BaseModel):
    text: str = Field(..., min_length=1, description="The feedback content cannot be empty")
    source: FeedbackSource
    customer_email: EmailStr

class FeedbackResponse(FeedbackCreate):
    id: UUID
    created_at: datetime
    category: str = "uncategorized"
    priority: str = "medium"

# In-memory storage (keyed by UUID)
feedback_db: Dict[UUID, FeedbackResponse] = {}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/feedback", response_model=FeedbackResponse, status_code=201)
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

@app.get("/feedback/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(feedback_id: UUID):
    if feedback_id not in feedback_db:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback_db[feedback_id]

@app.get("/feedback", response_model=List[FeedbackResponse])
def list_feedback(source: Optional[FeedbackSource] = Query(None, description="Filter by feedback source")):
    feedbacks = list(feedback_db.values())
    if source:
        feedbacks = [f for f in feedbacks if f.source == source]
    return feedbacks