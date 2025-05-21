# worker/heartbeat.py
import redis
import time
import os

worker_id = os.getenv("WORKER_ID", "worker-default")
r = redis.Redis(host="redis", port=6379, decode_responses=True)

def send_heartbeat():
    while True:
        r.setex(f"heartbeat:{worker_id}", 10, "alive")  # TTL 10s
        print(f"[HEARTBEAT] {worker_id} => alive")
        time.sleep(5)
