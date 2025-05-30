import redis
from utils.helper import REDIS_CLIENT

def get_active_workers():
    keys = REDIS_CLIENT.keys("heartbeat:*")
    return [key.split(":")[1] for key in keys]

def ping_redis():
    try:
        return REDIS_CLIENT.ping()
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        return False
