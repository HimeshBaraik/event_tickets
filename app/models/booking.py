from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime, Float
from app.core.db import Base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(Integer, ForeignKey("events.id"))
    seat_id = Column(Integer, ForeignKey("seats.id"))
    price = Column(Integer)

    # available, booked
    status = Column(String)

    __table_args__ = (
        UniqueConstraint("event_id", "seat_id", name="unique_event_seat"),
    )


class UserTicket(Base):
    __tablename__ = "user_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    
    status = Column(String, default="success")  # success, failed
    price_paid = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    
    reserved_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, default=datetime.utcnow)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(Integer, nullable=False)
    ticket_id = Column(Integer, nullable=False)
    reservation_id = Column(String, nullable=False)

    amount = Column(Integer, nullable=False)
    currency = Column(String, default="INR")

    status = Column(String, nullable=False, default="PENDING")

    payment_gateway = Column(String)
    gateway_order_id = Column(String, unique=True)
    gateway_payment_id = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)