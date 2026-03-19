# app/utils/utility.py
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Any, Optional
import json
import redis
import uuid
from email.mime.text import MIMEText
from app.core.config import settings

from app.models.booking import UserTicket
from app.core.email_templates import booking_success_template
from app.tasks.email_tasks import send_email_task

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

# Ticket Reserve and Confirm
def reserve_ticket(user_id: int, ticket_id: int, event_id: int, ttl: int = 600):
    reservation_id = str(uuid.uuid4())

    reservation_key = f"reservation:{reservation_id}"
    # lock_key = f"lock:ticket:{ticket_id}"

    value = json.dumps({
        "user_id": user_id,
        "ticket_id": ticket_id,
        "event_id": event_id,
        "reserved_at": datetime.utcnow().isoformat()
    })

    # lock_acquired = redis_client.set(lock_key, reservation_id, ex=ttl, nx=True)
    # if not lock_acquired:
    #     raise Exception("Ticket already reserved")

    # Store reservation
    redis_client.set(reservation_key, value, ex=ttl)

    return {
        "reservation_id": reservation_id,
        "expires_in": ttl
    }

def confirm_booking(db, ticket, user, reservation_key):
    # 1. Safety check
    # if ticket.status != "available":
    #     raise Exception("Ticket already booked")

    # 2. Update ticket
    ticket.status = "booked"
    db.add(ticket)

    # 3. Create booking
    user_ticket = UserTicket(
        user_id=user.id,
        ticket_id=ticket.id,
        event_id=ticket.event_id,
        price_paid=ticket.price,
        quantity=1,
        status="success",
        reserved_at=datetime.utcnow(),
        confirmed_at=datetime.utcnow()
    )
    db.add(user_ticket)

    # 4. Commit
    db.commit()

    # 5. Cleanup Redis
    redis_client.delete(reservation_key)
    redis_client.delete(f"lock:ticket:{ticket.id}")

    # 6. Async tasks
    subject, body = booking_success_template(
        user.name, ticket.id, "event"
    )

    send_email_task.delay(
        to_email=user.email,
        subject=subject,
        body=body
    )

    return user_ticket
