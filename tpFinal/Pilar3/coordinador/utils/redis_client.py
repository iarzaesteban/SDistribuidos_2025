import redis
from utils.helper import get_redis_connection

redis_client = get_redis_connection()

def get_active_workers():
    keys = redis_client.keys("heartbeat:*")
    return [key.split(":")[1] for key in keys]

def ping_redis():
    try:
        return redis_client.ping()
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        return False
