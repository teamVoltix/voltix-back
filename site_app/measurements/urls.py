from django.urls import path
from .views import index, get_all_measurements
from .userMeasurementListview import UserMeasurementListView

urlpatterns = [
    #path('', index, name='measurements_index'), 
    path('', UserMeasurementListView.as_view(), name='get_user_measurements'),  # Mediciones del usuario autenticado
    path('all/', get_all_measurements, name='get_all_measurements'),  # Todas las mediciones
]
