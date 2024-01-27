from django.urls import path, include
from facial_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('facial_attribute_analysis', views.facial_attribute_analysis, name='attribute-analysis'),
    path('compare_images', views.compare_images, name='compare-images'),
    path('face_verifications', views.face_verification, name='face-verification'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)