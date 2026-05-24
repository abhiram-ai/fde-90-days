import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env

load_dotenv()
db_url = os.environ.get("DATABASE_URL")

if not db_url:
    raise ValueError("DATABASE_URL environment variable is missing. Please set it in your environment variables.")

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Create a SQLAlchemy engine
engine = create_engine(db_url)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  