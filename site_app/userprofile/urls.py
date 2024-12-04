from django.urls import path
from . import views

urlpatterns = [
    path("",views.profile_view, name="profile_view"),
    path("update/", views.patch_profile, name="patch_profile"),
    path('upload-photo/', views.upload_profile_photo, name='upload_profile_photo'),
]
