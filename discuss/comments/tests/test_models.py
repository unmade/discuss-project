import pytest
from django.utils.encoding import force_text


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
