import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.logging_config import setup_logging
from app.routers import feedback, health


setup_logging()

app = FastAPI(
    title="Feedback API",
    description="A simple service to collect and categorize customer feedback"
)

# Enable CORS for the future frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to the specific dashboard URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

app.include_router(health.router)
app.include_router(feedback.router)
