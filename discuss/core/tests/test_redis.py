from unittest import mock

from django.conf import settings
from mockredis import MockRedis, mock_strict_redis_client

from core.redis import RedisClient


class TestRedisClient:

    def test_init(self):
        with mock.patch('redis.StrictRedis', mock_strict_redis_client):
            assert RedisClient(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)

    @mock.patch('redis.StrictRedis', return_value=mock_strict_redis_client())
    def test_get_client(self, redis_mock):
        redis_cli = RedisClient(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)
        client = redis_cli.get_client()
        assert isinstance(client, MockRedis)
