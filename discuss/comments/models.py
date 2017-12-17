from django.conf import settings
from django.db import models
from django.db.models.functions import Cast
from django.utils.translation import ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from users.models import User

# TODO: check indexes


class CommentQuerySet(models.QuerySet):

    def list_flat(self):
        return (
            self
            .select_related('author')
            # INFO: convert to datetime is slow, so casting to char
            .annotate(created_at_str=Cast('created_at', models.CharField()))
            .values(
                'id',
                'content',
                'parent_id',
                'content_type_id',
                'object_id',
                'author__email',
                'author__username',
                'created_at_str',
                'level',
            )
        )

    def not_deleted(self):
        return self.filter(is_deleted=False)


class Comment(MPTTModel):
    author = models.ForeignKey(User, verbose_name=_('Author'), related_name='comments', on_delete=models.CASCADE)

    content_type_id = models.IntegerField(_('Content type'))
    object_id = models.IntegerField(_('Object id'))

    parent = TreeForeignKey(
        'self',
        verbose_name=_('Parent comment'),
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(_('Date of creation'), auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(_('Date of modification'), auto_now=True)
    content = models.TextField(_('Content'), max_length=settings.COMMENT_CONTENT_MAX_LENGTH)

    is_deleted = models.BooleanField(_('Is deleted'), default=False)
    is_edited = models.BooleanField(_('Is edited'), default=False)

    objects = TreeManager.from_queryset(CommentQuerySet)()

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        index_together = [['content_type_id', 'object_id']]

    class MPTTMeta:
        order_insertion_by = ['created_at']

    def __str__(self):
        return f'{self.pk}'


# TODO: rename to History?
class CommentHistory(models.Model):
    CREATED = 0
    UPDATED = 1
    DELETED = 2
    ACTION_CHOICES = (
        (CREATED, _('Created')),
        (UPDATED, _('Updated')),
        (DELETED, _('Deleted')),
    )
    user = models.ForeignKey(User, verbose_name=_('User'), related_name='comments_history', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, verbose_name=_('Comment'), related_name='history', on_delete=models.CASCADE)
    content = models.TextField(_('Content'), blank=True)
    action = models.PositiveSmallIntegerField(_('Action'), choices=ACTION_CHOICES)
    created_at = models.DateTimeField(_('Date of creation'), auto_now_add=True)

    class Meta:
        verbose_name = _('Comment history')
        verbose_name_plural = _('Comments history')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.pk}'
