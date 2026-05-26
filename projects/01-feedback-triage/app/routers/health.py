from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("health_check_db_failure", exc_info=True)
        raise HTTPException(status_code=503, detail="DB is down")
    return {"status": "ok", "db": "ok"}
