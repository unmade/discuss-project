from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CommentsConfig(AppConfig):
    name = 'comments'
    verbose_name = _('Comment')

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals  # NOQA
