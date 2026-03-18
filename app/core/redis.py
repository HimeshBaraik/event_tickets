import redis
from app.core.config import settings

# Connect to Redis
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

# Test connection on import
try:
    redis_client.ping()
    print("Connected to Redis")
except redis.ConnectionError:
    print("Redis connection failed")