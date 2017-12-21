import pytest
from django.utils.encoding import force_text

from comments.models import Comment


class TestComment:

    @pytest.mark.django_db
    def test_string_representation(self, comment_factory):
        comment = comment_factory.create(parent=None)
        assert force_text(comment) == f'{comment.pk}'


class TestCommentHistory:

    @pytest.mark.django_db
    def test_string_representation(self, comment_history_factory):
        history = comment_history_factory.create()
        assert force_text(history) == f'{history.pk}'


class TestCommentQuerySet:

    @pytest.mark.django_db
    def test_count(self, comment_factory):
        comment_factory.create_batch(5, parent=None)
        assert Comment.objects.count() == 5

    @pytest.mark.django_db
    def test_chain_count(self, comment_factory):
        comment_factory.create_batch(5, parent=None)
        assert Comment.objects.list_flat().count() == 5

    @pytest.mark.django_db
    def test_count_with_filters(self, comment_factory):
        comment_factory.create_batch(2, parent=None)
        comment_factory.create_batch(3, parent=None, content_type_id=5)
        assert Comment.objects.list_flat().filter(content_type_id=1).count() == 2

    @pytest.mark.django_db
    def test_count_with_filter_on_related_object(self, comment_factory):
        from users.tests.conftest import UserFactory
        user = UserFactory.create()
        comment_factory.create_batch(2, parent=None)
        comment_factory.create_batch(3, parent=None, author=user)
        assert Comment.objects.filter(author__username=user).count() == 3
        assert Comment.objects.filter(author=user).count() == 3

    @pytest.mark.django_db
    def test_count_with_select_related(self, comment_factory):
        from users.tests.conftest import UserFactory
        user = UserFactory.create()
        comment_factory.create_batch(2, parent=None)
        comment_factory.create_batch(3, parent=None, author=user)
        assert Comment.objects.select_related('author').count() == 5
