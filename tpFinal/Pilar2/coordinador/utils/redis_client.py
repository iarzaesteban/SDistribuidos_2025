import os
import redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

def ping_redis():
    try:
        return redis_client.ping()
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        return False
