from django.urls import path
from . import views
from .login_view import LoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("", views.index, name="index"),
    path('register/', views.registro_usuario, name='registro_usuario'),
    path('login/', LoginView.as_view(), name='login'),
]
