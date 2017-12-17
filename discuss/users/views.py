from cent import generate_token, get_timestamp
from django.conf import settings
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from comments.models import Comment, CommentHistory
from comments.serializers import CommentHistorySerializer, FlatCommentSerializer
from .models import User
from .serializers import UserSerializer


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


class Token(APIView):

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.POST)
        serializer.is_valid(raise_exception=True)

        user, _ = User.objects.get_or_create(username=serializer.data.pop('username'), defaults=serializer.data)
        timestamp = get_timestamp()
        token = generate_token(settings.CENTRIFUGO_SECRET, user.username, timestamp, info='')

        return Response({
            'token': token,
            'timestamp': timestamp,
        })
