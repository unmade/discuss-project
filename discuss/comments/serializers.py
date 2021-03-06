from typing import Optional

import serpy
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from users.models import User
from users.serializers import UserSerializer

from . import comment_created, comment_updated
from .models import Comment, CommentHistory


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)

    class Meta:
        model = Comment
        fields = ['id', 'content_type_id', 'object_id', 'content', 'parent', 'created_at', 'author']

    def validate(self, data):
        parent = data.get('parent')  # type: Optional[Comment]
        if parent:
            if data['content_type_id'] != parent.content_type_id or data['object_id'] != parent.object_id:
                raise serializers.ValidationError(
                    _("`content_type_id` and `object_id` should equal to parent's ones")
                )

        return data


class CommentCreateUpdateSerializer(serializers.Serializer):
    comment = CommentSerializer()
    auth_user = UserSerializer()

    def validate(self, data):
        for field in ('comment', 'auth_user'):
            if field not in data:
                raise serializers.ValidationError(_(f'`{field}` field is required'))

        return data

    def create(self, validated_data):
        author_data = validated_data.pop('auth_user')
        username = author_data.pop('username')
        user, _ = User.objects.get_or_create(username=username, defaults=author_data)
        comment = Comment.objects.create(author=user, **validated_data['comment'])
        comment_created.send(sender=comment.__class__, comment=comment, user=user)
        return {
            'comment': comment,
            'auth_user': user,
        }

    def update(self, instance, validated_data):
        instance.content = validated_data['comment']['content']
        instance.save(update_fields=['content'])
        author_data = validated_data.pop('auth_user')
        username = author_data.pop('username')
        user, _ = User.objects.get_or_create(username=username, defaults=author_data)
        comment_updated.send(sender=instance.__class__, comment=instance, user=user)
        return {
            'comment': instance,
            'auth_user': user,
        }


class CommentDeleteSerializer(serializers.Serializer):
    auth_user = UserSerializer()


class CommentHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CommentHistory
        fields = ['id', 'action', 'comment_id', 'content', 'created_at', 'user']


class FlatCommentAuthorSerializer(serpy.DictSerializer):
    username = serpy.StrField(attr='author__username')
    email = serpy.StrField(attr='author__email')


class FlatCommentSerializer(serpy.DictSerializer):
    id = serpy.IntField()
    parent_id = serpy.IntField(required=False)
    content_type_id = serpy.IntField()
    object_id = serpy.IntField()
    created_at_str = serpy.StrField()
    content = serpy.StrField()
    level = serpy.IntField()
    author = serpy.MethodField()

    def get_author(self, obj):
        return FlatCommentAuthorSerializer(obj).data
