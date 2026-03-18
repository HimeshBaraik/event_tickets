# app/middleware.py
import uuid
from fastapi import FastAPI, Request

def register_middlewares(app: FastAPI):
    """
    Register all middlewares here using @app.middleware decorator
    """

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """
        Middleware to attach a unique request_id to each incoming request.
        The request_id is accessible in endpoints via request.state.request_id
        """
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        return response