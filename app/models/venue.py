from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.core.db import Base


class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)
    capacity = Column(Integer)


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False)
    row = Column(String, nullable=False)
    number = Column(Integer, nullable=False)
    seat_type = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint("venue_id", "row", "number", name="unique_seat_per_venue"),
    )