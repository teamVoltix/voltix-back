from django.urls import path
from .views import index, get_user_measurements, get_all_measurements

urlpatterns = [
    path('', index, name='measurements_index'), 
    path('search/', get_user_measurements, name='get_user_measurements'),  # Mediciones del usuario autenticado
    path('all/', get_all_measurements, name='get_all_measurements'),  # Todas las mediciones
]
