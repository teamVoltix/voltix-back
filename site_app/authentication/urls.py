from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import UserRegistrationView, LoginView
from .views import protected_view, logout_view, change_password_view, password_reset_request_view, password_reset_view



urlpatterns = [
    path("", views.index, name="index"),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/change-password/', change_password_view.as_view(), name='change_password'),
    path('password/reset/', password_reset_request_view, name='password_reset_request'),
    path('password/reset/<uidb64>/<token>/', password_reset_view, name='password_reset'),


    # paths de tokens and to do cheks
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', protected_view, name='protected'),
]
