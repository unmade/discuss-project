import pytest


class TestComment:

    @pytest.mark.django_db
    def test_clean_model_with_parent_id_from_another_thread(self, comment_factory):
        pass
