from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Comment, CommentHistory


@admin.register(Comment)
class CommentAdmin(MPTTModelAdmin):
    raw_id_fields = ['author', 'parent']
    list_select_related = ['author']
    list_display = ['id', 'content_type_id', 'object_id', 'created_at']


@admin.register(CommentHistory)
class CommentHistoryAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', 'comment']
    list_select_related = ['user']
    list_display = ['id', 'comment', 'created_at']
