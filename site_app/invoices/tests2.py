import os
import tempfile
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from voltix.models import Invoice, User
import datetime


class InvoiceTests(TestCase):
    """
    Pruebas básicas para las funcionalidades de facturas.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            dni="123456789", fullname="Test User", email="testuser@example.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.upload_url = reverse("invoice-upload")
        self.detail_url = lambda invoice_id: reverse("invoice_detail", args=[invoice_id])

        # Crear una factura para la prueba de detalle
        self.invoice = Invoice.objects.create(
            user=self.user,
            billing_period_start=datetime.date(2023, 1, 1),
            billing_period_end=datetime.date(2023, 1, 31),
            data={"key": "value"},
        )

    def test_upload_valid_pdf(self):
        """
        Probar que un archivo PDF válido se procesa correctamente.
        """
        with tempfile.NamedTemporaryFile(suffix=".pdf", mode="wb", delete=False) as temp_file:
            temp_file.write(b"%PDF-1.4 Valid PDF Content")
            temp_file.flush()  # Asegúrate de que los datos se escriben en disco
            temp_file.seek(0)

        # Abre el archivo nuevamente para leerlo con SimpleUploadedFile
        try:
            with open(temp_file.name, "rb") as file:
                uploaded_file = SimpleUploadedFile(
                    "test_invoice.pdf", file.read(), content_type="application/pdf"
                )
                response = self.client.post(self.upload_url, {"file": uploaded_file}, format="multipart")

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertIn("ocr_text", response.data)
            self.assertIn("parsed_data", response.data)
        finally:
            os.unlink(temp_file.name)  # Elimina el archivo temporal después de cerrar todos los manejadores


    def test_get_invoice_detail(self):
        """
        Probar que se puede obtener el detalle de una factura existente.
        """
        response = self.client.get(self.detail_url(self.invoice.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.invoice.id)
        self.assertEqual(response.data["user"], self.user.id)
