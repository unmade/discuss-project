import pytest
from django.urls import reverse
from rest_framework import status

from comments.tests.conftest import CommentHistoryFactory, CommentFactory
from users.models import User


class TestActionList:

    @pytest.mark.django_db
    def test_response_status_code_is_ok(self, client, user_factory):
        user = user_factory.create()
        CommentHistoryFactory.create_batch(10, user=user)
        url = reverse('users:actions', kwargs={'pk': user.pk})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_num_queries(self, client, django_assert_num_queries, user_factory):
        user = user_factory.create()
        CommentHistoryFactory.create_batch(10, user=user)
        url = reverse('users:actions', kwargs={'pk': user.pk})

        with django_assert_num_queries(2):
            client.get(url)

    @pytest.mark.django_db
    def test_filter_for_user(self, client, user_factory):
        user1 = user_factory.create()
        user2 = user_factory.create()
        CommentHistoryFactory.create_batch(5, user=user1)
        CommentHistoryFactory.create_batch(10, user=user2)
        url = reverse('users:actions', kwargs={'pk': user1.pk})
        response = client.get(url)

        content = response.json()
        assert len(content['results']) == 5


class TestHistoryList:

    @pytest.mark.django_db
    def test_response_status_code_is_ok(self, client, user_factory):
        user = user_factory.create()
        CommentFactory.create_batch(10, parent__parent__parent=None, author=user)
        url = reverse('users:comments', kwargs={'pk': user.pk})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_num_queries(self, client, django_assert_num_queries, user_factory):
        user = user_factory.create()
        CommentFactory.create_batch(10, parent__parent=None, author=user)
        url = reverse('users:comments', kwargs={'pk': user.pk})

        with django_assert_num_queries(2):
            client.get(url)

    @pytest.mark.django_db
    def test_filter_for_user(self, client, user_factory):
        user1 = user_factory.create()
        user2 = user_factory.create()
        CommentFactory.create_batch(5, parent__parent=None, author=user1)
        CommentFactory.create_batch(10, parent__parent__parent=None, author=user2)
        url = reverse('users:comments', kwargs={'pk': user1.pk})

        response = client.get(url)

        content = response.json()
        assert len(content['results']) == 5


class TestToken:

    @pytest.mark.django_db
    def test_response_status_code_is_ok(self, client, user_factory):
        user = user_factory.create()
        url = reverse('users:token')
        response = client.post(url, data={'username': user.username, 'email': user.email})
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_create_user_if_does_not_exists(self, client):
        url = reverse('users:token')
        response = client.post(url, data={'username': 'username', 'email': 'email@me.com'})
        assert response.status_code == status.HTTP_200_OK
        assert User.objects.count() == 1

    @pytest.mark.django_db
    def test_not_all_data_provided(self, client):
        url = reverse('users:token')
        response = client.post(url, data={'username': 'username'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'email': ['This field is required.']}
