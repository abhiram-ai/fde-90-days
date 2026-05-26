import re

from app.main import app
from app.database import get_db

def test_health_returns_ok(client):
    """Test that our API is alive and responding."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok"}


def test_health_returns_503_when_db_down(client):
    # Craft the "Broken" Database and the override function
    class BrokenDB:
        def execute(self, *args, **kwargs):
            raise Exception("Database is down")
        
    def override_get_db():
        yield BrokenDB()
    
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/health")
        assert response.status_code == 503
        assert response.json() == {"detail": "DB is down"}
    finally:
        app.dependency_overrides.clear()

