from django.urls import path

from . import views
from .views import InvoiceUploadView

urlpatterns = [
    path("", views.index, name="index"),
    path('upload/', InvoiceUploadView.as_view(), name='upload_invoice')
]
