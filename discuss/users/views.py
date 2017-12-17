from rest_framework import generics

from comments.models import Comment, CommentHistory
from comments.serializers import CommentHistorySerializer, FlatCommentSerializer


class ActionList(generics.ListAPIView):
    queryset = CommentHistory.objects.all().select_related('user')
    serializer_class = CommentHistorySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user_id=self.kwargs['pk'])


class CommentList(generics.ListAPIView):
    serializer_class = FlatCommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(author_id=self.kwargs['pk']).list_flat().not_deleted()
