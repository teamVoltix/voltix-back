from django.urls import path

from . import views
from .views import InvoiceUploadView, InvoiceSearchView

urlpatterns = [
    path("", views.index, name="index"),
    path('upload/', InvoiceUploadView.as_view(), name='upload_invoice'),
    path('search/', InvoiceSearchView.as_view(), name='search_invoice'),
]


# curl -X POST -F "file=@<RUTA_DE_ARCHIVO>" -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:8000/api/invoices/upload/
# curl -X POST -F "file=facturas/factura2.pdf>" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMyMTkzODMyLCJpYXQiOjE3MzIxOTI5MzIsImp0aSI6IjA4OGE5MWYwZmZmZTQ4M2I5MjYyODQzODZmZjgzZGNjIiwidXNlcl9pZCI6NDF9.fT26TiDgvOAxUdiszTMHzC89rIXQovPudhIzV9-Up38" http://127.0.0.1:8000/api/invoices/upload/