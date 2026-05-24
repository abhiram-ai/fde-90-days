from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import feedback, health


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

app.include_router(health.router)
app.include_router(feedback.router)



