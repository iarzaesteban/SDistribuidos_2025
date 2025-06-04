import redis
from utils.helper import REDIS_CLIENT


def ping_redis():
    try:
        return REDIS_CLIENT.ping()
    except redis.RedisError as e:
        print(f"Redis error: {e}")
        return False
