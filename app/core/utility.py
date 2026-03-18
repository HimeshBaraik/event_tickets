# app/utils/utility.py
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Any, Optional
import json
import redis
import smtplib
from email.mime.text import MIMEText
from app.core.config import settings


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


# Redis client
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


# Ticket Reserve and Confirm
def reserve_ticket(user_id: int, ticket_id: int, ttl: int = 600):
    """
    Create temporary reservation in Redis (10 mins default)
    """
    key = f"reservation:{user_id}:{ticket_id}"
    value = json.dumps({"user_id": user_id, "ticket_id": ticket_id})
    # NX ensures we don’t overwrite if key already exists
    success = redis_client.set(key, value, ex=ttl, nx=True)
    if not success:
        raise Exception("Ticket already reserved")
    return key

def confirm_ticket(user_id: int, ticket_id: int):
    """
    Confirm the reservation and delete it from Redis
    """
    key = f"reservation:{user_id}:{ticket_id}"
    data = redis_client.get(key)
    if not data:
        return None
    redis_client.delete(key)
    return json.loads(data)


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