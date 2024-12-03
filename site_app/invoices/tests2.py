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

    def test_upload_invalid_file_type(self):
        """
        Probar que subir un archivo con un tipo no válido genera un error.
        """
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="wb", delete=False) as temp_file:
            temp_file.write(b"Invalid Content")
            temp_file.flush()
            temp_file.seek(0)

        try:
            with open(temp_file.name, "rb") as file:
                uploaded_file = SimpleUploadedFile(
                    "test_invoice.txt", file.read(), content_type="text/plain"
                )
                response = self.client.post(self.upload_url, {"file": uploaded_file}, format="multipart")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("file", response.data["details"])
            self.assertIn("Invalid file type", str(response.data["details"]["file"]))
        finally:
            os.unlink(temp_file.name)

    def test_get_nonexistent_invoice_detail(self):
        """
        Probar que obtener el detalle de una factura inexistente devuelve un error 404.
        """
        nonexistent_id = 9999
        response = self.client.get(self.detail_url(nonexistent_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_upload_large_pdf_file(self):
        """
        Probar que subir un archivo PDF demasiado grande genera un error.
        """
        with tempfile.NamedTemporaryFile(suffix=".pdf", mode="wb", delete=False) as temp_file:
            temp_file.write(b"A" * (5 * 1024 * 1024 + 1))  # Generar un archivo de más de 5 MB
            temp_file.flush()
            temp_file.seek(0)

        try:
            with open(temp_file.name, "rb") as file:
                uploaded_file = SimpleUploadedFile(
                    "large_test_invoice.pdf", file.read(), content_type="application/pdf"
                )
                response = self.client.post(self.upload_url, {"file": uploaded_file}, format="multipart")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("file", response.data["details"])
            self.assertIn("File size exceeds 5 MB", str(response.data["details"]["file"]))
        finally:
            os.unlink(temp_file.name)

    def test_unauthorized_access(self):
        """
        Probar que un usuario no autenticado no puede acceder al endpoint de subida.
        """
        self.client.force_authenticate(user=None)  # Eliminar autenticación

        with tempfile.NamedTemporaryFile(suffix=".pdf", mode="wb", delete=False) as temp_file:
            temp_file.write(b"%PDF-1.4 Valid PDF Content")
            temp_file.flush()
            temp_file.seek(0)

        try:
            with open(temp_file.name, "rb") as file:
                uploaded_file = SimpleUploadedFile(
                    "test_invoice.pdf", file.read(), content_type="application/pdf"
                )
                response = self.client.post(self.upload_url, {"file": uploaded_file}, format="multipart")

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        finally:
            os.unlink(temp_file.name)
