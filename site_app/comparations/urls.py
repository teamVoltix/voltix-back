from django.urls import path
from . import views

urlpatterns = [
    path('compare/', views.compare_and_save, name='compare_and_save'),
]
