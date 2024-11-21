from django.urls import path

from . import views
from .views import InvoiceUploadView, InvoiceSearchView, InvoiceDetailView

urlpatterns = [
    path("", views.index, name="index"),
    path('upload/', InvoiceUploadView.as_view(), name='upload_invoice'),
    path('search/', InvoiceSearchView.as_view(), name='search_invoice'),
    path('<int:invoice_id>/', InvoiceDetailView.as_view(), name='invoice_detail'),
]


# curl -X POST -F "file=@<RUTA_DE_ARCHIVO>" -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:8000/api/invoices/upload/
# curl -X POST -F "file=facturas/factura2.pdf>" -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:8000/api/invoices/upload/
