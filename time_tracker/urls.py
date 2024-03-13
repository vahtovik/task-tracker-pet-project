from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls', namespace='main_app')),
    path('', include('users.urls', namespace='users')),
]
