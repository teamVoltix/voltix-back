from django.urls import path
from . import views

urlpatterns = [
    path('usuarios/', views.get_all_users, name='get_all_users'),
]
