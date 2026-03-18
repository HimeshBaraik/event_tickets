from fastapi import APIRouter, Request
from app.core.utility import set_key, get_key
from app.core.utility import default_response

router = APIRouter()

@router.get("/redis/set")
def set_redis(request: Request):
    set_key("foo", "bar")
    return default_response(message="Key 'foo' set to 'bar' in Redis", request=request)

@router.get("/redis/get")
def get_redis(request: Request):
    value = get_key("foo")
    return default_response(data={"foo": value or "Key not found"}, request=request)