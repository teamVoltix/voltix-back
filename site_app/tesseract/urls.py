from django.urls import path
from . import views

urlpatterns = [
    path('process/', views.process_invoice, name='process_invoice'),
]
