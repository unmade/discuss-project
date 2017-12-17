from django.urls import path

from . import views

app_name = 'users'


urlpatterns = [
    path('<int:pk>/actions/', views.ActionList.as_view(), name='actions'),
    path('<int:pk>/comments/', views.CommentList.as_view(), name='comments'),
    path('token/', views.Token.as_view(), name='token')
]
