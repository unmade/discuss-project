import django_filters

from .models import Comment


class CommentFilter(django_filters.FilterSet):
    created = django_filters.DateTimeFromToRangeFilter(name='created_at')
    username = django_filters.CharFilter(name='author__username')
    user = django_filters.NumberFilter(name='author_id')

    class Meta:
        model = Comment
        fields = ['content_type_id', 'object_id', 'user', 'username', 'created']
