import json

from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework import generics, status
from rest_framework.response import Response

from core.outputters.mixins import OutputMixin
from users.models import User
from .filters import CommentFilter
from .models import Comment, CommentHistory
from .outputters import CommentOutputter
from .serializers import (
    CommentCreateUpdateSerializer, CommentDeleteSerializer, CommentHistorySerializer, FlatCommentSerializer
)
from .signals import comment_deleted


class CommentList(generics.ListAPIView):
    serializer_class = FlatCommentSerializer
    filter_class = CommentFilter

    def get_queryset(self):
        with_children = self.request.GET.get('with_children', False)
        qs = Comment.objects

        if not with_children:
            qs = qs.root_nodes()

        return qs.not_deleted().list_flat()


class CommentChildren(generics.ListAPIView):
    serializer_class = FlatCommentSerializer
    pagination_class = None

    def get_queryset(self):
        try:
            comment = Comment.objects.get(pk=self.kwargs['pk'])
        except Comment.DoesNotExist:
            raise Http404

        return comment.get_descendants().list_flat().not_deleted()


class CommentHistoryList(generics.ListAPIView):
    queryset = CommentHistory.objects.all().select_related('user')
    serializer_class = CommentHistorySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(comment_id=self.kwargs['pk'])


class CommentCreate(generics.CreateAPIView):
    serializer_class = CommentCreateUpdateSerializer


class CommentUpdate(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateUpdateSerializer
    http_method_names = ['patch']


class CommentDelete(generics.DestroyAPIView):
    queryset = Comment.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()  # type: Comment

        if instance.get_descendant_count():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'error': _('Could not delete parent comment')}
            )

        try:
            data = json.loads(request.body)  # INFO: request.POST is empty on DELETE
        except json.JSONDecodeError as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'error': _('JSON decode error')}
            )

        serializer = CommentDeleteSerializer(data=data)
        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors,
            )

        username = serializer.data['user'].pop('username')
        user, is_created = User.objects.get_or_create(username=username, defaults=serializer.data['user'])
        self.perform_destroy(instance)
        comment_deleted.send(sender=instance.__class__, comment=instance, user=user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])


class CommentDownload(OutputMixin, CommentList):
    outputter_class = CommentOutputter
    filename = 'comments'
