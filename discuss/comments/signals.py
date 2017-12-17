from django.dispatch import Signal, receiver

from .models import CommentHistory, Comment

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


@receiver(comment_created, sender=Comment)
def log_comment_created(comment, user, **kwargs):
    _log_comment_changes(CommentHistory.CREATED, comment, user)


@receiver(comment_updated, sender=Comment)
def log_comment_updated(comment, user, **kwargs):
    _log_comment_changes(CommentHistory.UPDATED, comment, user)


@receiver(comment_deleted, sender=Comment)
def log_comment_deleted(comment, user, **kwargs):
    _log_comment_changes(CommentHistory.DELETED, comment, user)
