import pytest
from django.urls import reverse
from rest_framework import status

from comments.tests.conftest import CommentHistoryFactory, CommentFactory


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
