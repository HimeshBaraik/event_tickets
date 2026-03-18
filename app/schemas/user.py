# serialization + deserialization + validation schemas for User model

from pydantic import BaseModel, EmailStr


# Signup Schema
class UserCreate(BaseModel):
    name: str
    email: EmailStr   # validates email format
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True  # allows returning SQLAlchemy object


# Login Schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str