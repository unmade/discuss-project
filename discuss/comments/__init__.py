from django.dispatch import Signal

default_app_config = 'comments.apps.CommentsConfig'

comment_created = Signal(providing_args=['comment', 'user'])
comment_updated = Signal(providing_args=['comment', 'user'])
comment_deleted = Signal(providing_args=['comment', 'user'])
