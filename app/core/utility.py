# app/utils/utility.py
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Any, Optional
import redis
import smtplib
import uuid
from email.mime.text import MIMEText
from app.core.config import settings

from app.models.booking import UserTicket
from app.core.email_templates import booking_success_template

# default response
def default_response(
    data: Any = None,
    message: str = "Success",
    request: Optional[Request] = None,
    status_code: int = 200
) -> dict:
    """
    custom response format for all API responses.
    """
    meta = {
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    if request:
        meta.update({
            "request_id": getattr(request.state, "request_id", None),
            "path": request.url.path
        })

    output = {
        "data": data,
        "message": message,
        "meta": meta
    }
    return output


# Redis operations
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def set_key(key: str, value: str, expire: int = None):
    """
    Set a key in Redis with optional expiry (in seconds)
    """
    redis_client.set(key, value, ex=expire)
    return True

def get_key(key: str):
    """
    Get a key value from Redis
    """
    return redis_client.get(key)

def delete_key(key: str):
    """
    Delete a key from Redis
    """
    redis_client.delete(key)
    return True


# mail sending utility
def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = "your_email@gmail.com"
    msg["To"] = to_email
    print(f"[UTILITY] Sending email to {to_email}")

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
        server.send_message(msg)