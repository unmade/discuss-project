import json

from django.dispatch import Signal, receiver

from core.redis import redis_cli
from users.serializers import UserSerializer
from .models import Comment, CommentHistory
from .serializers import CommentSerializer

comment_created = Signal(providing_args=['comment', 'user'])
comment_updated = Signal(providing_args=['comment', 'user'])
comment_deleted = Signal(providing_args=['comment', 'user'])


def _log_comment_changes(action, comment, user):
    CommentHistory.objects.create(
        action=action,
        comment=comment,
        content=comment.content,
        user=user,
    )


def _notify(action, comment, user):
    command = {
        'method': 'publish',
        'params': {
            'channel': f'thread:{comment.content_type_id}_{comment.object_id}',
            'data': {
                'comment': CommentSerializer(comment).data,
                'user': UserSerializer(user).data,
                'action': action,
            }
        }
    }

    client = redis_cli.get_client()
    client.rpush('centrifugo.api', json.dumps(command))


@receiver(comment_created, sender=Comment)
def log_comment_created(comment, user, **kwargs):
    _log_comment_changes(CommentHistory.CREATED, comment, user)


@receiver(comment_updated, sender=Comment)
def log_comment_updated(comment, user, **kwargs):
    _log_comment_changes(CommentHistory.UPDATED, comment, user)


@receiver(comment_deleted, sender=Comment)
def log_comment_deleted(comment, user, **kwargs):
    _log_comment_changes(CommentHistory.DELETED, comment, user)


@receiver(comment_created, sender=Comment)
def notify_comment_created(comment, user, **kwargs):
    _notify(CommentHistory.CREATED, comment, user)


@receiver(comment_updated, sender=Comment)
def notify_comment_updated(comment, user, **kwargs):
    _notify(CommentHistory.UPDATED, comment, user)


@receiver(comment_deleted, sender=Comment)
def notify_comment_deleted(comment, user, **kwargs):
    _notify(CommentHistory.DELETED, comment, user)
