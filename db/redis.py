import redis
from config.settings import REDIS_HOST, REDIS_PORT

def initialize_redis():
    try:
        redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        print("Redis initialized successfully.")
        return redis_client
    except Exception as e:
        print(f"Error initializing Redis: {e}")
