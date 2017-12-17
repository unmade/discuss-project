import redis
from django.conf import settings


class RedisClient:

    def __init__(self):
        self.__client = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )

    def get_client(self):
        return self.__client


redis_cli = RedisClient()
