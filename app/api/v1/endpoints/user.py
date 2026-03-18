from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.db import get_db
from app.models.user import User
from app.crud.auth import store_refresh_token
from app.schemas.user import UserCreate, UserResponse
from app.schemas.user import UserLogin
from app.crud.user import get_user_by_email
from app.core.db import get_db
from app.core.security import hash_password, verify_password, obtain_token_pair, decode_token
from app.core.utility import default_response

from app.api.v1.message import UserMessages, AuthMessages

# Create router
router = APIRouter()

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Signup API:
    - Takes user input
    - Stores in DB
    - Returns created user
    """

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user object
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password= hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(user: UserLogin, request: Request, db: Session = Depends(get_db)):

    db_user = get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token, refresh_token = obtain_token_pair(db_user.id)

    # store refresh token in DB with expiry
    payload = decode_token(refresh_token)
    exp = datetime.fromtimestamp(payload["exp"])

    store_refresh_token(db, db_user.id, refresh_token, exp)

    data= {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

    return default_response(data=data, message=AuthMessages.LOGIN_SUCCESS, request=request)


@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh API:
    1. Validate refresh token
    2. Check in DB
    3. Issue new access + refresh tokens (rotation)
    """

    # 1️⃣ Decode token and validate
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user_id = int(payload["sub"])

    # 2️⃣ Check if refresh token exists in DB
    db_token = get_refresh_token(db, refresh_token)
    if not db_token or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    # 3️⃣ Delete old refresh token (rotation)
    db.delete(db_token)
    db.commit()

    # 4️⃣ Issue new access + refresh tokens
    access_token, new_refresh_token = obtain_token_pair(user_id)

    # 5️⃣ Decode new refresh to get expiry
    new_payload = decode_token(new_refresh_token)
    exp = datetime.fromtimestamp(new_payload["exp"])

    # 6️⃣ Store new refresh token in DB
    store_refresh_token(db, user_id, new_refresh_token, exp)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


# @router.post("/logout")
# def logout(current_user=Depends(get_current_user), token: str = Depends(get_token_from_header), db: Session = Depends(get_db)):
#     """
#     Logout API
#     1. Add access token jti to blacklist
#     2. Delete all refresh tokens of this user (optional)
#     """
#     payload = decode_token(token)
#     jti = payload["jti"]

#     # 1. blacklist current access token
#     blacklist_token(db, jti, datetime.fromtimestamp(payload["exp"]))

#     # 2. delete all refresh tokens of this user
#     db.query(RefreshToken).filter(RefreshToken.user_id == current_user.id).delete()
#     db.commit()

#     return {"detail": "Logged out successfully"}