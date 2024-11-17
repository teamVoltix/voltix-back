from django.urls import path
from . import views
from .login_view import LoginView
from rest_framework_simplejwt.views import TokenRefreshView
from .protected_endpoint_view import ProtectedEndpointView

urlpatterns = [
    path("", views.index, name="index"),
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected-endpoint/', ProtectedEndpointView.as_view(), name='protected_endpoint'),

]
