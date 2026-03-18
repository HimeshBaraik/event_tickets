from app.models.auth import RefreshToken
from sqlalchemy.orm import Session

def store_refresh_token(db: Session, user_id: int, token: str, expires_at):
    db_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()