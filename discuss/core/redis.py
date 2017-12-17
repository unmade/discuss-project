import redis
from django.conf import settings
from django.utils.functional import SimpleLazyObject


class RedisClient:

    def __init__(self, host, port, db):
        self.__client = redis.StrictRedis(host=host, port=port, db=db)

    def get_client(self):
        return self.__client


redis_cli = SimpleLazyObject(
    lambda: RedisClient(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)
)
