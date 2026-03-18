from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models.user import User


def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(user_id: int):
    db = SessionLocal()
    return db.query(User).filter(User.id == user_id).first()