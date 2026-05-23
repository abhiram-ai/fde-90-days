# Feedback Triage API

A lightweight FastAPI service to collect and centralize customer feedback from multiple channels (Email, Slack, App, etc.). 
It assigns unique IDs and timestamps, standardizes the payload, and makes it available for future dashboard triage.

## Setup & Installation

This project requires Python 3.11+ and uses `pydantic` for strict validation (including emails).

1. **Install dependencies:**
   ```bash
   pip install "fastapi[all]" "pydantic[email]"
   ```
   *(Note: `fastapi[all]` includes `uvicorn` for running the server).*

2. **Run the server locally:**
   ```bash
   uvicorn main:app --reload
   ```
   The API will start on `http://127.0.0.1:8000`.

## Endpoints & `curl` Examples

### 1. Health Check
Verify the deployment is running smoothly.
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

### 2. Submit New Feedback
Accepts feedback and provisions a new tracked record.
```bash
curl -X POST "http://127.0.0.1:8000/feedback" \
     -H "Content-Type: application/json" \
     -d '{
           "text": "This feature is exactly what we needed!",
           "source": "app",
           "customer_email": "jane@example.com"
         }'
```

### 3. Get All Feedback
Retrieve all feedback currently in the in-memory store. You can also filter by `source`.
```bash
# Retrieve all
curl -X GET "http://127.0.0.1:8000/feedback"

# Filter strictly by email source
curl -X GET "http://127.0.0.1:8000/feedback?source=email"
```

### 4. Get a Single Feedback Record
Retrieve a specific feedback payload by its UUID.
```bash
# Be sure to replace the UUID with a valid ID from your POST request!
curl -X GET "http://127.0.0.1:8000/feedback/123e4567-e89b-12d3-a456-426614174000"
```