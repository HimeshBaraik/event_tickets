'''
Main entry point for the FastAPI application.
This file initializes the FastAPI app and includes all the necessary routes.
'''

from fastapi import FastAPI
from sqlalchemy import engine

from app.api.v1.endpoints import events
from app.core.db import Base, engine
from app.api.v1.api import api_router

from app.middleware import register_middlewares
from app.models import *
Base.metadata.create_all(bind=engine)

# Create FastAPI app instance
app = FastAPI()

# Register all middlewares
register_middlewares(app)


# Test endpoint to check if the backend is running
@app.get("/")
def root():
    return {"message": "Backend is running"}

# Include API router (all our endpoints will be under /api/v1)
app.include_router(api_router, prefix="/api/v1")