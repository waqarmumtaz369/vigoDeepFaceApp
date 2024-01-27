from django.contrib import admin
from django.urls import path, include
from facial_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('facial_app.urls')),
]
