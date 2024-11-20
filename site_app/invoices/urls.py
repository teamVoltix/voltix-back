from django.urls import path

from . import views
from .views import InvoiceUploadView

urlpatterns = [
    path("", views.index, name="index"),
    path('upload/', InvoiceUploadView.as_view(), name='upload_invoice')
]


# curl -X POST -F "file=@<RUTA_DE_ARCHIVO>" -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:8000/api/invoices/upload/
