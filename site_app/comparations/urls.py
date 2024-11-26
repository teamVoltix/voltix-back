from django.urls import path
from . import views

urlpatterns = [
    path('compare/', views.compare_invoice_and_measurement, name='compare_and_save'),
    
]
