from django.urls import path
from . import views
from .userComparisonListview import UserComparisonDetailView, UserComparisonListView


urlpatterns = [
    path('compare/', views.compare_invoice_and_measurement, name='compare_and_save'),
    path('comparisons/', UserComparisonListView.as_view(), name='user-comparisons'),
    path('comparisons/<int:comparison_id>/', UserComparisonDetailView.as_view(), name='user_comparison_detail'),
]