from django.urls import path
from . import views


urlpatterns = [
    path('compare/', views.compare_invoice_and_measurement, name='compare_and_save'),
    path('comparisons/<int:comparison_id>/', views.UserComparisonDetailView.as_view(), name='user_comparison_detail'),
]