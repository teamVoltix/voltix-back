from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='users_index'),  # Ruta para el índice
    path('get_all_users/', views.get_all_users, name='get_all_users'),  # Ruta para get_all_users
]
