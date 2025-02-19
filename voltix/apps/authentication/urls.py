from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import UserRegistrationView, LoginView
from .views import protected_view, logout_view, ChangePasswordView, password_reset_request_view, password_reset_view, DeleteUserView, DeactivateAccountView, public_reactivate_account
# nueva logica de registracion
from .validation_views import (
    RequestVerificationCodeView,
    ValidateVerificationCodeView,
    RegistrationView, 
)
from .tokenRefreshView import CustomTokenRefreshView



urlpatterns = [
    path("", views.index, name="index"),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('password/reset/', password_reset_request_view, name='password_reset_request'),
    path('password/reset/<uidb64>/<token>/', password_reset_view, name='password_reset'),
    path('users/delete/<int:user_id>/', DeleteUserView.as_view(), name='delete_user'),
    #path('deactivate/', DeactivateAccountView.as_view(), name='deactivate_account'),
    #path('reactivate/', public_reactivate_account, name='public_reactivate_account'),

    # paths de tokens and to do cheks + con fns de Django
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #cusrom refresh/ token function
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    path('protected/', protected_view, name='protected'),

    #nuevas rutas de nueva logica de registracion con validacion
    path('email-verification/request/', RequestVerificationCodeView.as_view(), name='request_verification_code'),
    path('email-verification/validate/', ValidateVerificationCodeView.as_view(), name='validate_verification_code'),
    path('email-verification/register/', RegistrationView.as_view(), name='email_verification_register'),
]
