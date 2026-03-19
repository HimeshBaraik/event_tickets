from fastapi import APIRouter, Depends, HTTPException, Request
from app.core import db
from app.core.utility import default_response
from app.core.book_utility import reserve_ticket, confirm_booking
from app.core.security import get_current_user
from app.core.db import SessionLocal
from app.core.utility import redis_client
from app.core.email_templates import booking_success_template
from app.tasks.email_tasks import send_email_task

from app.models import Ticket, Event
from app.api.v1.message import BookTicketMessages
from app.models.booking import UserTicket
from datetime import datetime

router = APIRouter()

@router.post("/{ticket_id}")
def reserve(
    ticket_id: int,
    request: Request,
    current_user = Depends(get_current_user)
):
    """
    Temporarily reserve a ticket using Redis (with lock)
    """
    db = SessionLocal()

    try:
        # 1. Check if ticket exists
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=404,
                detail=BookTicketMessages.TICKET_NOT_FOUND.value
            )

        # 2. Check availability
        # if ticket.status != "available":
        #     raise HTTPException(
        #         status_code=400,
        #         detail=BookTicketMessages.TICKET_UNAVAILABLE.value
        #     )

        # 3. Reserve ticket in Redis (new format)
        reservation_data = reserve_ticket(
            user_id=current_user.id,
            ticket_id=ticket.id,
            event_id=ticket.event_id
        )

        # 4. Return response
        return default_response(
            data={
                "reservation_id": reservation_data["reservation_id"],
                "expires_in": reservation_data["expires_in"]
            },
            message=BookTicketMessages.TICKET_RESERVED.value
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        db.close()


@router.post("/{ticket_id}/confirm")
def confirm(ticket_id: int, request: Request, current_user=Depends(get_current_user)):
    """
    Confirm a reserved ticket (payment simulation + DB update)
    """

    db = SessionLocal()

    # Check if ticket exists
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail=BookTicketMessages.TICKET_NOT_FOUND.value)
    
    event = db.query(Event).filter(Event.id == ticket.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=BookTicketMessages.EVENT_NOT_FOUND.value)   

    # Check reservation exists in Redis and belongs to current user
    reservation_key = f"reservation:{current_user.id}:{ticket_id}"
    reserved_data = redis_client.get(reservation_key)
    if not reserved_data:
        raise HTTPException(status_code=400, detail=BookTicketMessages.RESERVATION_EXPIRED.value)

    # Simulate payment process
    payment_successful = True  # Replace with actual payment integration
    if not payment_successful:
        raise HTTPException(status_code=402, detail=BookTicketMessages.PAYMENT_FAILED.value)

    # 4. Update ticket status to 'booked'
    # if ticket.status != "available":
    #     raise HTTPException(status_code=400, detail=BookTicketMessages.TICKET_UNAVAILABLE.value)
    
    try:
        # 1. Update ticket status so other users cannot reserve it
        ticket.status = "booked"
        db.add(ticket)
        
        # Create user ticket entry
        user_ticket = UserTicket(
            user_id=current_user.id,
            ticket_id=ticket.id,
            event_id=ticket.event_id,
            price_paid=ticket.price,
            quantity=1,
            status="success",
            reserved_at=datetime.utcnow(),
            confirmed_at=datetime.utcnow()
        )
        db.add(user_ticket)

        # 3. Commit both changes in a single transaction
        db.commit()
        db.refresh(ticket)
        db.refresh(user_ticket)

        # 6. Delete reservation from Redis
        redis_client.delete(reservation_key)


        subject, body = booking_success_template(current_user.name, ticket.id, event.name)

        send_email_task.delay(
            to_email=current_user.email,
            subject=subject,
            body=body
        )
        
        # 7. Return success response
        return default_response(
            message=BookTicketMessages.TICKET_CONFIRMED.value,
            data={
                "ticket_id": ticket.id,
                "booking_id": user_ticket.id,
                "status": user_ticket.status
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")