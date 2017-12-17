import json
from datetime import datetime
from unittest import mock

import pytest
import pytz
from django.urls import reverse
from mockredis import mock_strict_redis_client
from rest_framework import status

from comments.models import CommentHistory
from core.redis import RedisClient


class TestCommentList:
    url = reverse('comments:list')

    @pytest.mark.django_db
    def test_response_status_code_is_ok(self, client, comment_factory):
        comment_factory.create_batch(5, parent__parent=None)
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_comments_filtered_by_instance(self, client, comment_factory):
        size = 5
        comment_factory.create_batch(size, parent__parent=None)
        comment_factory.create_batch(size, parent=None, content_type_id=2, object_id=2)

        response = client.get(self.url, {'content_type_id': 1, 'object_id': 1})
        content = response.json()

        assert len(content['results']) == size

    @pytest.mark.django_db
    def test_num_queries(self, client, django_assert_num_queries, comment_factory):
        comment_factory.create_batch(10, parent__parent__parent__parent=None)

        with django_assert_num_queries(2):
            client.get(self.url)

    @pytest.mark.django_db
    def test_no_deleted_in_list(self, client, comment_factory):
        comment_factory.create_batch(3, parent=None)
        comment_factory.create_batch(5, parent=None, is_deleted=True)

        response = client.get(self.url)
        content = response.json()

        assert len(content['results']) == 3


class TestCommentListWithChildren:
    url = reverse('comments:list')

    @pytest.mark.django_db
    def test_response_status_code_is_ok(self, client, comment_factory):
        comment_factory.create_batch(10, parent__parent=None)
        response = client.get(self.url, {'with_children': True})
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_num_queries(self, client, django_assert_num_queries, comment_factory):
        comment_factory.create_batch(10, parent__parent__parent__parent=None)

        with django_assert_num_queries(2):
            client.get(self.url, {'with_children': True})

    @pytest.mark.django_db
    def test_no_deleted_in_list(self, client, comment_factory):
        comment = comment_factory.create(parent__parent__parent=None)
        comment.is_deleted = True
        comment.save(update_fields=['is_deleted'])

        response = client.get(self.url, {'with_children': True})
        content = response.json()

        assert len(content['results']) == 2


class TestCommentChildren:

    @pytest.mark.django_db
    def test_response_status_code_is_ok(self, client, comment_factory):
        comment = comment_factory.create(parent__parent__parent=None)
        url = reverse('comments:children', kwargs={'pk': comment.parent.parent.pk})

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        content = response.json()
        assert len(content) == 2

    @pytest.mark.django_db
    def test_num_queries(self, client, django_assert_num_queries, comment_factory):
        comment = comment_factory.create(parent__parent__parent__parent__parent=None)
        url = reverse('comments:children', kwargs={'pk': comment.parent.parent.parent.parent.pk})

        with django_assert_num_queries(2):
            client.get(url)

    @pytest.mark.django_db
    def test_no_deleted_in_list(self, client, comment_factory):
        comment = comment_factory.create(parent__parent__parent=None)
        comment.is_deleted = True
        comment.save(update_fields=['is_deleted'])

        url = reverse('comments:children', kwargs={'pk': comment.parent.pk})
        response = client.get(url)
        content = response.json()

        assert len(content) == 0

    @pytest.mark.django_db
    def test_non_existing_comment(self, client):
        url = reverse('comments:children', kwargs={'pk': 1})
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCommentCreate:
    url = reverse('comments:create')

    @pytest.fixture
    def comment_data(self):
        return {
            'comment': {
                'content_type_id': 1,
                'object_id': 1,
                'content': 'Really good comment',
            },
            'user': {
                'email': 'email@example.com',
                'username': 'user1234',
            },
        }

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_comment_create(self, redis_mock, client, comment_data):
        response = client.post(self.url, data=json.dumps(comment_data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    @pytest.mark.parametrize('key', ['comment', 'user'])
    def test_comment_and_user_is_required(self, client, comment_data, key):
        comment_data.pop(key)
        response = client.post(self.url, data=json.dumps(comment_data), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {key: ['This field is required.']}

    @pytest.mark.django_db
    def test_create_comment_with_non_existing_parent(self, client, comment_data):
        comment_data['comment']['parent'] = -1
        response = client.post(self.url, data=json.dumps(comment_data), content_type='application/json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'comment': {'parent': ['Invalid pk "-1" - object does not exist.']}}

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_create_reply_to_comment(self, redis_mock, client, comment_factory, comment_data):
        comment = comment_factory.create(parent=None)
        comment_data['comment'].update({
            'content_type_id': comment.content_type_id,
            'object_id': comment.object_id,
            'parent': comment.pk
        })

        response = client.post(self.url, data=json.dumps(comment_data), content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    @pytest.mark.parametrize(['content_type_id', 'object_id', 'expected_status'], [
        (1, 10, status.HTTP_400_BAD_REQUEST),
        (10, 1, status.HTTP_400_BAD_REQUEST),
        (10, 10, status.HTTP_400_BAD_REQUEST),
    ])
    def test_create_reply_to_comment_with_different_thread(
            self, client, comment_factory, comment_data, content_type_id, object_id, expected_status
    ):
        comment = comment_factory.create(parent=None)
        comment_data['comment'].update({
            'content_type_id': content_type_id,
            'object_id': object_id,
            'parent': comment.pk
        })

        response = client.post(self.url, data=json.dumps(comment_data), content_type='application/json')
        assert response.status_code == expected_status

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_create_history_record_on_comment_create(self, redis_mock, client, comment_data):
        response = client.post(self.url, data=json.dumps(comment_data), content_type='application/json')
        content = response.json()

        comment_id = content['comment']['id']
        history = CommentHistory.objects.get(comment_id=comment_id)

        assert history.action == CommentHistory.CREATED
        assert history.content == content['comment']['content']
        assert history.user.username == comment_data['user']['username']

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_send_notification_on_comment_create(self, redis_mock, client, comment_data):
        client.post(self.url, data=json.dumps(comment_data), content_type='application/json')
        assert redis_mock.called

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_same_user_can_create_comment_more_than_once(self, redis_mock, client, comment_data):
        for _ in range(2):
            response = client.post(self.url, data=json.dumps(comment_data), content_type='application/json')
            assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_ignore_user_email_if_user_already_exists(self, redis_mock, client, comment_data):
        client.post(self.url, data=json.dumps(comment_data), content_type='application/json')

        old_email = comment_data['user']['email']
        comment_data['user']['email'] = 'another@mail.me'
        response = client.post(self.url, data=json.dumps(comment_data), content_type='application/json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['user']['email'] == old_email


class TestCommentUpdate:

    @pytest.fixture
    def update_data(self):
        return {
            'comment': {
                'content': 'Edited!',
            },
            'user': {
                'email': 'example@email.com',
                'username': 'user4321',
            },
        }

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_comment_update(self, redis_mock, client, comment_factory, update_data):
        comment = comment_factory.create(parent=None)

        url = reverse('comments:update', kwargs={'pk': comment.pk})
        response = client.patch(url, data=json.dumps(update_data), content_type='application/json')

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    @pytest.mark.parametrize('key', ['comment', 'user'])
    def test_comment_and_user_is_required(self, client, comment_factory, update_data, key):
        update_data.pop(key)
        comment = comment_factory.create(parent=None)

        url = reverse('comments:update', kwargs={'pk': comment.pk})
        response = client.patch(url, data=json.dumps(update_data), content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'non_field_errors': [f'`{key}` field is required']}

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_comment_update_updates_only_content(self, redis_mock, client, comment_factory):
        comment = comment_factory.create(parent=None)
        url = reverse('comments:update', kwargs={'pk': comment.pk})
        data = {
            'comment': {
                'content_type_id': 10,
                'object_id': 10,
                'content': 'Edited!Again',
                'author': {
                    'email': 'example@email.com',
                    'username': 'user4321',
                },
            },
            'user': {
                'email': 'example@email.com',
                'username': 'user4321',
            },
        }

        response = client.patch(url, data=json.dumps(data), content_type='application/json')
        content = response.json()
        comment_data = content['comment']

        assert comment_data['content_type_id'] == 1
        assert comment_data['object_id'] == 1
        assert comment_data['content'] == 'Edited!Again'
        assert comment_data['author']['username'] == comment.author.username
        assert comment_data['author']['email'] == comment.author.email

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_create_history_record_on_comment_update(self, redis_mock, client, comment_factory, update_data):
        comment = comment_factory.create(parent=None)

        url = reverse('comments:update', kwargs={'pk': comment.pk})
        response = client.patch(url, data=json.dumps(update_data), content_type='application/json')

        content = response.json()
        comment_id = content['comment']['id']
        history = CommentHistory.objects.get(comment_id=comment_id)

        assert history.action == CommentHistory.UPDATED
        assert history.content == update_data['comment']['content']
        assert history.user.username == update_data['user']['username']

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_send_notification_on_comment_update(self, redis_mock, client, comment_factory, update_data):
        comment = comment_factory.create(parent=None)

        url = reverse('comments:update', kwargs={'pk': comment.pk})
        client.patch(url, data=json.dumps(update_data), content_type='application/json')

        assert redis_mock.called

    @pytest.mark.django_db
    def test_comment_update_put_is_not_allowed(self, client, comment_factory, update_data):
        comment = comment_factory.create(parent=None)

        url = reverse('comments:update', kwargs={'pk': comment.pk})
        response = client.put(url, data=json.dumps(update_data), content_type='application/json')

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_same_user_can_update_comment_more_than_once(self, redis_mock, client, comment_factory, update_data):
        for _ in range(2):
            comment = comment_factory.create(parent=None)

            url = reverse('comments:update', kwargs={'pk': comment.pk})
            response = client.patch(url, data=json.dumps(update_data), content_type='application/json')
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_ignore_user_email_if_user_already_exists(self, redis_mock, client, comment_factory, update_data):
        comment = comment_factory.create(parent=None)

        url = reverse('comments:update', kwargs={'pk': comment.pk})
        client.patch(url, data=json.dumps(update_data), content_type='application/json')

        old_email = update_data['user']['email']
        update_data['user']['email'] = 'another@mail.me'

        response = client.patch(url, data=json.dumps(update_data), content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['user']['email'] == old_email


class TestCommentDelete:

    @pytest.fixture
    def user_data(self):
        return {
            'user': {
                'email': 'example@email.com',
                'username': 'user4321',
            }
        }

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_comment_delete(self, redis_mock, client, comment_factory, user_data):
        comment = comment_factory.create(parent=None)

        url = reverse('comments:delete', kwargs={'pk': comment.pk})
        response = client.delete(url, data=json.dumps(user_data), content_type='application/json')

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.django_db
    def test_no_data_send(self, client, comment_factory):
        comment = comment_factory.create(parent=None)

        url = reverse('comments:delete', kwargs={'pk': comment.pk})
        response = client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'error': 'JSON decode error'}

    @pytest.mark.django_db
    def test_user_is_required(self, client, comment_factory):
        comment = comment_factory.create(parent=None)

        url = reverse('comments:delete', kwargs={'pk': comment.pk})
        response = client.delete(url, data=json.dumps({'content': '1'}), content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'user': ['This field is required.']}

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_comment_delete_do_not_delete_from_database(self, redis_mock, client, comment_factory, user_data):
        comment = comment_factory.create(parent=None)
        url = reverse('comments:delete', kwargs={'pk': comment.pk})

        client.delete(url, data=json.dumps(user_data), content_type='application/json')
        comment.refresh_from_db()

        assert comment.is_deleted is True

    @pytest.mark.django_db
    def test_comment_delete_do_not_delete_parent_comment(self, client, comment_factory, user_data):
        comment = comment_factory.create(parent__parent=None)

        url = reverse('comments:delete', kwargs={'pk': comment.parent.pk})
        response = client.delete(url, data=json.dumps(user_data), content_type='application/json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'error': 'Could not delete parent comment'}

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_create_history_record_on_comment_delete(self, redis_mock, client, comment_factory, user_data):
        comment = comment_factory.create(parent=None)

        url = reverse('comments:delete', kwargs={'pk': comment.pk})
        client.delete(url, data=json.dumps(user_data), content_type='application/json')

        history = CommentHistory.objects.get(comment_id=comment.pk)
        assert history.action == CommentHistory.DELETED
        assert history.content == comment.content
        assert history.user.username == user_data['user']['username']

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_send_notification_on_comment_delete(self, redis_mock, client, comment_factory, user_data):
        comment = comment_factory.create(parent=None)

        url = reverse('comments:delete', kwargs={'pk': comment.pk})
        client.delete(url, data=json.dumps(user_data), content_type='application/json')

        assert redis_mock.called

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_same_user_can_delete_comment_more_than_once(self, redis_mock, client, comment_factory, user_data):
        for _ in range(2):
            comment = comment_factory.create(parent=None)

            url = reverse('comments:delete', kwargs={'pk': comment.pk})
            response = client.delete(url, data=json.dumps(user_data), content_type='application/json')
            assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.django_db
    @mock.patch.object(RedisClient, 'get_client', return_value=mock_strict_redis_client())
    def test_ignore_user_email_if_user_already_exists(self, redis_mock, client, comment_factory, user_data):
        comment = comment_factory.create(parent=None)

        url = reverse('comments:delete', kwargs={'pk': comment.pk})
        response = client.delete(url, data=json.dumps(user_data), content_type='application/json')
        assert response.status_code == status.HTTP_204_NO_CONTENT

        user_data['user']['email'] = 'another@mail.me'

        comment = comment_factory.create(parent=None)
        url = reverse('comments:delete', kwargs={'pk': comment.pk})
        response = client.delete(url, data=json.dumps(user_data), content_type='application/json')
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestCommentHistoryList:

    @pytest.mark.django_db
    def test_comment_history(self, client, comment_factory, comment_history_factory):
        comment = comment_factory.create(parent=None)
        comment_history_factory.create_batch(5, comment=comment)

        url = reverse('comments:history', kwargs={'pk': comment.pk})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_num_queries(self, client, django_assert_num_queries, comment_factory, comment_history_factory):
        comment = comment_factory.create(parent=None)
        comment_history_factory.create_batch(5, comment=comment)

        url = reverse('comments:history', kwargs={'pk': comment.pk})

        with django_assert_num_queries(2):
            client.get(url)

    @pytest.mark.django_db
    def test_filter_by_comment_id(self, client, comment_factory, comment_history_factory):
        comment1 = comment_factory.create(parent=None)
        comment2 = comment_factory.create(parent=None)
        comment_history_factory.create_batch(3, comment=comment1)
        comment_history_factory.create_batch(5, comment=comment2)

        url = reverse('comments:history', kwargs={'pk': comment1.pk})
        response = client.get(url)
        content = response.json()

        assert len(content['results']) == 3


class TestCommentDownload:

    @pytest.mark.django_db
    def test_response_status_is_ok(self, client, comment_factory):
        comment_factory.create_batch(2, parent=None)

        url = reverse('comments:download')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert list(response.streaming_content)
        assert response['Content-Type'] == 'text/xml'

    @pytest.mark.django_db
    def test_unsupported_format(self, client):
        url = reverse('comments:download')
        response = client.get(url, {'output': 'pdf'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'error': 'Unsupported output format.'}

    @pytest.mark.django_db
    def test_filter_by_date_range(self, client, comment_factory):
        comment_factory.create_batch(2, parent=None, created_at=datetime(2017, 1, 1, tzinfo=pytz.UTC))
        comment_factory.create_batch(2, parent=None, created_at=datetime(2017, 2, 2, tzinfo=pytz.UTC))
        comment_factory.create_batch(2, parent=None, created_at=datetime(2017, 3, 3, tzinfo=pytz.UTC))
        url = reverse('comments:download')
        response = client.get(url, {'created_0': '2017-2-1', 'created_1': '2017-3-1'})

        assert response.status_code == status.HTTP_200_OK
        assert len(list(response.streaming_content)) == 2
