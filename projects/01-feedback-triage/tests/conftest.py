import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base, Feedback, FeedbackSource

# Using standard postgresql:// because we are using psycopg2-binary
TEST_DATABASE_URL = "postgresql://feedback:feedback@localhost:5432/feedback_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def test_db():
    """Creates a fresh test database for each test and drops it after."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client(test_db):
    """A test client that overrides the get_db dependency to use the test database."""
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture()
def sample_feedback(test_db):
    """A factory fixture that creates a record and returns its ID."""
    feedback = Feedback(
        text="This is a test feedback from the factory fixture.",
        source=FeedbackSource.app,
        customer_email="test.factory@example.com"
    )
    test_db.add(feedback)
    test_db.commit()
    test_db.refresh(feedback)
    return feedback.id