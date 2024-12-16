# import os
# import tempfile
# from django.test import TestCase
# from django.urls import reverse
# from django.core.files.uploadedfile import SimpleUploadedFile
# from rest_framework.test import APIClient
# from rest_framework import status
# from django.core.exceptions import ValidationError
# from voltix.models import Invoice, User
# import datetime


# class InvoiceTests(TestCase):
#     """
#     Pruebas básicas para las funcionalidades de facturas.
#     """

#     def setUp(self):
#         """
#         Configuración inicial para las pruebas.
#         """
#         self.client = APIClient()
#         self.user = User.objects.create_user(
#             dni="123456789", fullname="Test User", email="testuser@example.com", password="password123"
#         )
#         self.client.force_authenticate(user=self.user)

#         self.upload_url = reverse("invoice-upload")
#         self.detail_url = lambda invoice_id: reverse("invoice_detail", args=[invoice_id])

#         # Crear una factura para la prueba de detalle
#         self.invoice = Invoice.objects.create(
#             user=self.user,
#             billing_period_start=datetime.date(2023, 1, 1),
#             billing_period_end=datetime.date(2023, 1, 31),
#             data={"key": "value"},
#         )

#     def test_upload_valid_pdf(self):
#         """
#         Probar que un archivo PDF válido se procesa correctamente.
#         """
#         with tempfile.NamedTemporaryFile(suffix=".pdf", mode="wb", delete=False) as temp_file:
#             temp_file.write(b"%PDF-1.4 Valid PDF Content")
#             temp_file.flush()  # Asegúrate de que los datos se escriben en disco
#             temp_file.seek(0)

#         try:
#             with open(temp_file.name, "rb") as file:
#                 uploaded_file = SimpleUploadedFile(
#                     "test_invoice.pdf", file.read(), content_type="application/pdf"
#                 )
#                 response = self.client.post(self.upload_url, {"file": uploaded_file}, format="multipart")

#             self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#             self.assertIn("ocr_text", response.data)
#             self.assertIn("parsed_data", response.data)
#         finally:
#             os.unlink(temp_file.name)  # Elimina el archivo temporal después de cerrar todos los manejadores

#     def test_get_invoice_detail(self):
#         """
#         Probar que se puede obtener el detalle de una factura existente.
#         """
#         response = self.client.get(self.detail_url(self.invoice.id))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["id"], self.invoice.id)
#         self.assertEqual(response.data["user"], self.user.id)

#     def test_upload_invalid_file_type(self):
#         """
#         Probar que subir un archivo con un tipo no válido genera un error.
#         """
#         with tempfile.NamedTemporaryFile(suffix=".txt", mode="wb", delete=False) as temp_file:
#             temp_file.write(b"Invalid Content")
#             temp_file.flush()
#             temp_file.seek(0)

#         try:
#             with open(temp_file.name, "rb") as file:
#                 uploaded_file = SimpleUploadedFile(
#                     "test_invoice.txt", file.read(), content_type="text/plain"
#                 )
#                 response = self.client.post(self.upload_url, {"file": uploaded_file}, format="multipart")

#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#             self.assertIn("file", response.data["details"])
#             self.assertIn("Invalid file type", str(response.data["details"]["file"]))
#         finally:
#             os.unlink(temp_file.name)

#     def test_get_nonexistent_invoice_detail(self):
#         """
#         Probar que obtener el detalle de una factura inexistente devuelve un error 404.
#         """
#         nonexistent_id = 9999
#         response = self.client.get(self.detail_url(nonexistent_id))
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_upload_large_pdf_file(self):
#         """
#         Probar que subir un archivo PDF demasiado grande genera un error.
#         """
#         with tempfile.NamedTemporaryFile(suffix=".pdf", mode="wb", delete=False) as temp_file:
#             temp_file.write(b"A" * (5 * 1024 * 1024 + 1))  # Generar un archivo de más de 5 MB
#             temp_file.flush()
#             temp_file.seek(0)

#         try:
#             with open(temp_file.name, "rb") as file:
#                 uploaded_file = SimpleUploadedFile(
#                     "large_test_invoice.pdf", file.read(), content_type="application/pdf"
#                 )
#                 response = self.client.post(self.upload_url, {"file": uploaded_file}, format="multipart")

#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#             self.assertIn("file", response.data["details"])
#             self.assertIn("File size exceeds 5 MB", str(response.data["details"]["file"]))
#         finally:
#             os.unlink(temp_file.name)

#     def test_unauthorized_access(self):
#         """
#         Probar que un usuario no autenticado no puede acceder al endpoint de subida.
#         """
#         self.client.force_authenticate(user=None)  # Eliminar autenticación

#         with tempfile.NamedTemporaryFile(suffix=".pdf", mode="wb", delete=False) as temp_file:
#             temp_file.write(b"%PDF-1.4 Valid PDF Content")
#             temp_file.flush()
#             temp_file.seek(0)

#         try:
#             with open(temp_file.name, "rb") as file:
#                 uploaded_file = SimpleUploadedFile(
#                     "test_invoice.pdf", file.read(), content_type="application/pdf"
#                 )
#                 response = self.client.post(self.upload_url, {"file": uploaded_file}, format="multipart")

#             self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         finally:
#             os.unlink(temp_file.name)

#     def test_invoice_date_validation(self):
#         """
#         Probar que el rango de fechas en las facturas se valida correctamente.
#         """
#         # Caso positivo: Fechas válidas
#         try:
#             invoice = Invoice(
#                 user=self.user,
#                 billing_period_start=datetime.date(2023, 1, 1),
#                 billing_period_end=datetime.date(2023, 1, 31),
#             )
#             invoice.clean()  # No debería lanzar excepción
#         except ValidationError:
#             self.fail("El método clean lanzó ValidationError inesperadamente para fechas válidas.")

#         # Caso negativo: Fecha de inicio después de la fecha de fin
#         with self.assertRaises(ValidationError):
#             invoice = Invoice(
#                 user=self.user,
#                 billing_period_start=datetime.date(2023, 2, 1),
#                 billing_period_end=datetime.date(2023, 1, 31),
#             )
#             invoice.clean()

# """
# Explicación de cada test y como ejecutarlo:

# 1. **`test_upload_valid_pdf`**:
#    Verifica que el sistema acepta y procesa correctamente un archivo PDF válido. Confirma que los datos como el texto OCR y los datos parseados se devuelven correctamente.

# 2. **`test_get_invoice_detail`**:
#    Verifica que se puede obtener el detalle de una factura existente por su ID. Comprueba que los datos coincidan con los esperados.

# 3. **`test_upload_invalid_file_type`**:
#    Verifica que el sistema rechaza archivos con extensiones o tipos MIME no permitidos (por ejemplo, `.txt`). Comprueba que se genera un error 400 con el mensaje adecuado.

# 4. **`test_get_nonexistent_invoice_detail`**:
#    Comprueba que intentar obtener el detalle de una factura que no existe devuelve un error 404, asegurando que el sistema maneja casos de elementos inexistentes correctamente.

# 5. **`test_upload_large_pdf_file`**:
#    Verifica que el sistema rechaza un archivo PDF que excede el tamaño máximo permitido (5 MB). Confirma que se genera un error 400 con el mensaje adecuado.

# 6. **`test_unauthorized_access`**:
#    Asegura que un usuario no autenticado no puede acceder al endpoint de subida de facturas, devolviendo un error 401.

# 7. **`test_invoice_date_validation`**:
#    Valida el rango de fechas de facturación:
#    - **Positivo:** Fechas válidas no generan errores.
#    - **Negativo:** Fechas inválidas (inicio después del fin) generan un `ValidationError`.

# Ejecutar los tests:
#     python site_app/manage.py test invoices.tests2 --keepdb
# """
