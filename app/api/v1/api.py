from fastapi import APIRouter
from app.api.v1.endpoints import booking, test_redis, user, events

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(test_redis.router, prefix="/redis", tags=["Redis"])
api_router.include_router(booking.router, prefix="/booking", tags=["Booking"])