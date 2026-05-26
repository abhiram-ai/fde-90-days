from urllib import response

import pytest
from app.models import FeedbackSource

def test_create_feedback_returns_201_with_id(client):
    """Test that we can successfully create a new feedback entry."""
    payload = {
        "text": "This is a great app!",
        "source": "app",
        "customer_email": "user@example.com"
    }
    response = client.post("/feedback/", json=payload)
    
    assert response.status_code == 201, (
        f"Expected 201, got {response.status_code}: {response.text}"
    )
    data = response.json()
    assert "id" in data

def test_create_feedback_rejects_empty_text(client):
    """Test that an empty text field returns a 422 error."""
    payload = {
        "text": "",
        "source": "app",
    }

    response = client.post("/feedback/", json=payload)
    assert response.status_code == 422

def test_create_feedback_rejects_invalid_source(client):
    """Test that an invalid source returns a 422 error."""
    payload = {
        "text": "Invalid source test",
        "source": "carrier-pigeon",
        "customer_email": "user@example.com"
    }

    response = client.post("/feedback/", json=payload)
    assert response.status_code == 422

def test_create_feedback_allows_null_email(client):
    """Test that a null email is allowed."""
    payload = {
        "text": "Null email test",
        "source": "app",
    }

    response = client.post("/feedback/", json=payload)
    assert response.status_code == 201
    data = response.json()
    #print(data)
    assert data['customer_email'] is None

def test_get_feedback_returns_404_when_not_found(client):
    """Get UUID that doesn't exist"""
    response = client.get("/feedback/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert "detail" in  response.json()
    assert "not found" in response.json()["detail"].lower()

def test_get_feedback_returns_422_for_malformed_id(client):
    """A non-UUID path parameter should be rejected by validation, 
    not treated as 'not found'."""
    response = client.get("/feedback/not-a-uuid")
    print(response)
    assert response.status_code == 422

def test_list_feedback_filters_by_source(client):
    """Test that the list endpoint correctly filters by source. Seed the database with two different sources"""
    client.post("/feedback/", json={"text": "App feedback", "source": "app"})
    client.post("/feedback/", json={"text": "Slack feedback", "source": "slack"})

    # 2. Fetch the filtered list
    response = client.get("/feedback/?source=app")
    
    # 3. Assert only the matching record is returned
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["source"] == "app"

def test_patch_feedback_updates_reviewed_flag(client):
    """PATCH /feedback/{id} with reviewed=true should update the record
    and the change should persist on subsequent GETs."""
    
    # Arrange: create a record and confirm it starts unreviewed
    payload = {
        "text": "This is a great app!",
        "source": "app",
        "customer_email": "user@example.com"
    }
    create_response = client.post("/feedback/", json=payload)
    assert create_response.status_code == 201, f"Setup failed: {create_response.json()}"
    feedback_id = create_response.json()["id"]
    assert create_response.json()["reviewed"] is False
    
    # Act: patch the reviewed flag
    patch_response = client.patch(
        f"/feedback/{feedback_id}",
        json={"reviewed": True}
    )
    
    # Assert: response reflects the change
    assert patch_response.status_code == 200
    assert patch_response.json()["reviewed"] is True
    
    # Assert: change persisted to the database
    get_response = client.get(f"/feedback/{feedback_id}")
    assert get_response.status_code == 200
    assert get_response.json()["reviewed"] is True

def test_patch_feedback_returns_404_when_not_found(client):
    """PATCH /feedback/{id} not found should return 404."""
    response = client.patch(
        "/feedback/00000000-0000-0000-0000-000000000000",
        json={"reviewed": True}
    )
    assert response.status_code == 404, (
        f"Expected 404 for nonexistent id, got {response.status_code}: {response.text}"
    )
    assert "detail" in  response.json()
    assert "not found" in response.json()["detail"].lower()