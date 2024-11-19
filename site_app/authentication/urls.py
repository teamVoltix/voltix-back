from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import registro_usuario, login_view, protected_view
#user_profile, logout_view

urlpatterns = [
    path("", views.index, name="index"),
    path('register/', views.registro_usuario, name='registro_usuario'),
    path('login/', login_view, name='login'),
    # path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('protected/', protected_view, name='protected'),
    # path('profile/', user_profile, name='user_profile'),
    # path('logout/', logout_view, name='logout'),
]
