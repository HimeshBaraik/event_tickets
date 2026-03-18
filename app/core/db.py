from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create connection to Postgres
engine = create_engine(settings.DATABASE_URL)

# Session = DB connection per request
SessionLocal = sessionmaker(bind=engine)

# Base = parent for all tables
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()