from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from app.core.db import Base


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    genre = Column(String)
    bio = Column(Text)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, index=True)
    description = Column(Text)

    artist_id = Column(Integer, ForeignKey("artists.id"))
    venue_id = Column(Integer, ForeignKey("venues.id"))

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    total_seats = Column(Integer)
    available_seats = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)