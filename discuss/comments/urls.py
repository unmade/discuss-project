from django.urls import path

from . import views

app_name = 'comments'

urlpatterns = [
    path('list/', views.CommentList.as_view(), name='list'),

    path('list/export/', views.CommentExport.as_view(), name='export'),

    path('<int:pk>/children/', views.CommentChildren.as_view(), name='children'),
    path('<int:pk>/history/', views.CommentHistoryList.as_view(), name='history'),
    path('<int:pk>/update/', views.CommentUpdate.as_view(), name='update'),
    path('<int:pk>/delete/', views.CommentDelete.as_view(), name='delete'),

    path('create/', views.CommentCreate.as_view(), name='create'),
]
