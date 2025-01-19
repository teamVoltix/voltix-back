from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("",views.profile_view, name="profile_view"),
    path("update/", views.patch_profile, name="patch_profile"),
    path('upload-photo/', views.upload_profile_photo, name='upload_profile_photo'),
]

if settings.DEBUG:  #development only
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)