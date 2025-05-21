import os
import redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

def get_active_workers():
    keys = redis_client.keys("heartbeat:*")
    return [key.split(":")[1] for key in keys]

def ping_redis():
    try:
        return redis_client.ping()
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        return False
