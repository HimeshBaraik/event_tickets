from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user

# Router = group of related APIs
router = APIRouter()


@router.get("/events")
def list_events(current_user = Depends(get_current_user)):
    """
    Returns all events.
    Only accessible if user provides a valid JWT access token.
    """
    # current_user is verified and available
    return ["hello"]