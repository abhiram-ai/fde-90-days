from datetime import datetime, timezone
from typing import Optional
import uuid
from enum import Enum
from sqlalchemy import String, DateTime, func, false
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class FeedbackSource(str, Enum):
    email = "email"
    slack = "slack"
    app = "app"
    other = "other"

class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True,default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String(5000))
    source: Mapped[FeedbackSource] = mapped_column(index=True)
    customer_email: Mapped[Optional[str]] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="uncategorized",server_default="uncategorized", index=True)   
    priority: Mapped[str] = mapped_column(String(50), default="medium",server_default="medium") 
    reviewed: Mapped[bool] = mapped_column(default=False, server_default=false(), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),server_default=func.now(),onupdate=lambda: datetime.now(timezone.utc))