import time

from redis import Redis

from db.redis import redis

if __name__ == '__main__':
    redis_client = Redis(hosts='http://localhost', port=6379)
    while True:
        if redis_client.ping():
            break
        time.sleep(1)