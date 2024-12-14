# import os
# import uuid
# import tempfile
# import shutil
# from django.test import TestCase
# from django.urls import reverse
# from django.core.files.uploadedfile import SimpleUploadedFile
# from rest_framework.test import APIClient
# from rest_framework import status
# from django.conf import settings
# from voltix.models import User, Invoice


# class InvoiceProcessViewTests(TestCase):
#     """
#     Pruebas unitarias para las vistas de procesamiento de facturas.
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

#         self.process_url = reverse("invoice-process")  # Ajusta el nombre de la ruta
#         self.test_pdf_path = os.path.join(tempfile.gettempdir(), "test_invoice.pdf")

#         # Crear un archivo PDF temporal para las pruebas
#         with open(self.test_pdf_path, "wb") as f:
#             f.write(b"%PDF-1.4 test invoice pdf content")

#         # Configurar carpeta temporal
#         self.temp_folder = settings.FILE_UPLOAD_TEMP_DIR or os.path.join(settings.BASE_DIR, "media", "temp")
#         if not os.path.exists(self.temp_folder):
#             os.makedirs(self.temp_folder)

#     def tearDown(self):
#         """
#         Limpieza después de cada prueba.
#         """
#         if os.path.exists(self.test_pdf_path):
#             os.remove(self.test_pdf_path)
#         shutil.rmtree(self.temp_folder, ignore_errors=True)

#     def test_upload_valid_pdf(self):
#         """
#         Probar que un archivo PDF válido se procesa correctamente.
#         """
#         with open(self.test_pdf_path, "rb") as f:
#             file = SimpleUploadedFile("test_invoice.pdf", f.read(), content_type="application/pdf")
#             response = self.client.post(self.process_url, {"file": file}, format="multipart")
        
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertIn("invoice_id", response.data)
#         self.assertIn("parsed_data", response.data)
#         self.assertGreater(response.data["processed_images_count"], 0)

#     def test_upload_file_with_incorrect_extension(self):
#         """
#         Probar que un archivo con una extensión incorrecta genera un error.
#         """
#         with open(self.test_pdf_path, "rb") as f:
#             file = SimpleUploadedFile("test_invoice.txt", f.read(), content_type="text/plain")
#             response = self.client.post(self.process_url, {"file": file}, format="multipart")
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("file", response.data)
#         self.assertIn("Invalid file type", response.data["details"]["file"][0])

#     def test_upload_large_file(self):
#         """
#         Probar que un archivo muy grande genera un error.
#         """
#         large_file_path = os.path.join(tempfile.gettempdir(), "large_test_invoice.pdf")
#         with open(large_file_path, "wb") as f:
#             f.write(b"A" * (5 * 1024 * 1024 + 1))  # Archivo de más de 5 MB

#         with open(large_file_path, "rb") as f:
#             file = SimpleUploadedFile("large_test_invoice.pdf", f.read(), content_type="application/pdf")
#             response = self.client.post(self.process_url, {"file": file}, format="multipart")
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("file", response.data)
#         self.assertIn("File size exceeds 5 MB", response.data["details"]["file"][0])

#         os.remove(large_file_path)

#     def test_unauthenticated_access_to_upload_invoice(self):
#         """
#         Probar que un usuario no autenticado no puede acceder al endpoint de subida.
#         """
#         self.client.force_authenticate(user=None)  # Quitar autenticación
#         with open(self.test_pdf_path, "rb") as f:
#             file = SimpleUploadedFile("test_invoice.pdf", f.read(), content_type="application/pdf")
#             response = self.client.post(self.process_url, {"file": file}, format="multipart")
        
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_json_data_validation_on_database(self):
#         """
#         Probar que el JSON guardado en la base de datos tiene los campos esperados.
#         """
#         with open(self.test_pdf_path, "rb") as f:
#             file = SimpleUploadedFile("test_invoice.pdf", f.read(), content_type="application/pdf")
#             response = self.client.post(self.process_url, {"file": file}, format="multipart")
        
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         invoice_id = response.data["invoice_id"]
#         invoice = Invoice.objects.get(pk=invoice_id)
#         self.assertIn("nombre_cliente", invoice.data)
#         self.assertIn("periodo_facturacion", invoice.data)
#         self.assertIn("desglose_cargos", invoice.data)

#     def test_concurrent_uploads(self):
#         """
#         Probar el comportamiento del sistema con múltiples usuarios subiendo facturas al mismo tiempo.
#         """
#         def upload_file(user, file_path):
#             self.client.force_authenticate(user=user)
#             with open(file_path, "rb") as f:
#                 file = SimpleUploadedFile("test_invoice.pdf", f.read(), content_type="application/pdf")
#                 return self.client.post(self.process_url, {"file": file}, format="multipart")

#         users = [
#             User.objects.create_user(dni=f"12345678{index}", fullname=f"User {index}", email=f"user{index}@test.com", password="password123")
#             for index in range(5)
#         ]
        
#         responses = []
#         for user in users:
#             response = upload_file(user, self.test_pdf_path)
#             responses.append(response)
        
#         for response in responses:
#             self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_partial_processing_of_images_in_pdf(self):
#         """
#         Probar que el sistema maneja errores en imágenes intermedias y procesa las restantes.
#         """
#         def mock_process_image(self, image_data):
#             # Simular un error en la segunda imagen
#             if len(image_data) % 2 == 0:
#                 raise ValueError("Error procesando imagen.")
#             return image_data

#         # Parchar el método para esta prueba
#         from site_app.invoices.views import InvoiceProcessView
#         InvoiceProcessView.process_image = mock_process_image

#         with open(self.test_pdf_path, "rb") as f:
#             file = SimpleUploadedFile("test_invoice.pdf", f.read(), content_type="application/pdf")
#             response = self.client.post(self.process_url, {"file": file}, format="multipart")
        
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertGreater(response.data["processed_images_count"], 0)  # Asegurarse de que al menos algunas imágenes fueron procesadas

#     def test_temp_files_cleanup(self):
#         """
#         Probar que los archivos temporales se eliminan después del procesamiento.
#         """
#         initial_files = set(os.listdir(self.temp_folder)) if os.path.exists(self.temp_folder) else set()

#         with open(self.test_pdf_path, "rb") as f:
#             file = SimpleUploadedFile("test_invoice.pdf", f.read(), content_type="application/pdf")
#             response = self.client.post(self.process_url, {"file": file}, format="multipart")
        
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         final_files = set(os.listdir(self.temp_folder)) if os.path.exists(self.temp_folder) else set()
#         self.assertEqual(initial_files, final_files)  # Verifica que no hay nuevos archivos temporales
