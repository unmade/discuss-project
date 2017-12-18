from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    path('comments/', include('comments.urls', namespace='comments')),
    path('users/', include('users.urls', namespace='users')),
]
