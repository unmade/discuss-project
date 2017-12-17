from cent import generate_token, get_timestamp
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
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
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.POST)
        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors
            )

        user = get_object_or_404(User, username=serializer.data['username'])
        timestamp = get_timestamp()
        token = generate_token(settings.CENTRIFUGO_SECRET, user.username, timestamp, info='')

        return Response({
            'token': token,
            'timestamp': timestamp,
        })
