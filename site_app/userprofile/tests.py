from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from voltix.models import User, Profile
from django.db import connections
from PIL import Image
import io


def generate_test_image():
    """
    Genera un archivo de imagen válido en memoria.
    """
    img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    return buffer.getvalue()


class UploadProfilePhotoTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        # Cierra las conexiones activas para evitar problemas de eliminación
        super().tearDownClass()
        for conn in connections.all():
            conn.close()

    def setUp(self):
        # Configurar cliente API y usuario
        self.client = APIClient()
        self.user = User.objects.create_user(
            fullname="Test User",
            dni="123456789",
            email="test@example.com",
            password="Test1234!"
        )
        # Usa `get_or_create` para evitar duplicados
        self.profile, created = Profile.objects.get_or_create(
            user=self.user,
            defaults={"photo_url": ""}
        )
        self.client.force_authenticate(user=self.user)  # Autenticar al usuario

    @patch('userprofile.views.upload')
    def test_upload_profile_photo_success(self, mock_upload):
        # Simula una subida exitosa
        mock_upload.return_value = {
            "secure_url": "https://example.com/test-photo.jpg"
        }

        # Crear un archivo simulado válido
        test_image = SimpleUploadedFile(
            "test_image.jpg",
            generate_test_image(),
            content_type="image/jpeg"
        )

        response = self.client.post(
            reverse('upload_profile_photo'),
            {'photo': test_image},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Foto subida exitosamente.")
        self.assertIn('photo_url', response.data)

    def test_upload_profile_photo_no_file(self):
        # Enviar solicitud sin archivo
        response = self.client.post(
            reverse('upload_profile_photo'),
            {},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "No se encontró un archivo para subir.")

    def test_upload_profile_photo_no_profile(self):
        # Eliminar el perfil del usuario
        self.profile.delete()

        # Crear un archivo simulado
        test_image = SimpleUploadedFile(
            "test_image.jpg",
            generate_test_image(),
            content_type="image/jpeg"
        )

        response = self.client.post(
            reverse('upload_profile_photo'),
            {'photo': test_image},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "El perfil no existe.")

    @patch('userprofile.views.upload')
    def test_upload_profile_photo_cloudinary_error(self, mock_upload):
        # Simula un error de Cloudinary
        mock_upload.side_effect = Exception("Cloudinary error")

        # Crear un archivo simulado válido
        test_image = SimpleUploadedFile(
            "test_image.jpg",
            generate_test_image(),
            content_type="image/jpeg"
        )

        response = self.client.post(
            reverse('upload_profile_photo'),
            {'photo': test_image},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Error de Cloudinary", response.data['error'])

    def test_upload_profile_photo_invalid_file_type(self):
        # Crear un archivo simulado con un tipo no permitido
        invalid_file = SimpleUploadedFile(
            "test_file.txt",
            b"This is a text file, not an image",
            content_type="text/plain"
        )

        response = self.client.post(
            reverse('upload_profile_photo'),
            {'photo': invalid_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Tipo de archivo no válido.")

    def test_upload_profile_photo_large_file(self):
        # Crear un archivo simulado muy grande
        large_file = SimpleUploadedFile(
            "large_image.jpg",
            b"0" * (10 * 1024 * 1024),  # 10 MB
            content_type="image/jpeg"
        )

        response = self.client.post(
            reverse('upload_profile_photo'),
            {'photo': large_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "El archivo excede el tamaño máximo permitido de 5 MB.")

    def test_upload_profile_photo_unauthenticated(self):
        # Desautenticar al usuario
        self.client.force_authenticate(user=None)

        # Crear un archivo simulado
        test_image = SimpleUploadedFile(
            "test_image.jpg",
            generate_test_image(),
            content_type="image/jpeg"
        )

        response = self.client.post(
            reverse('upload_profile_photo'),
            {'photo': test_image},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    @patch('userprofile.views.upload')
    def test_upload_profile_photo_cloudinary_quota_exceeded(self, mock_upload):
        # Simula un error de cuota excedida
        mock_upload.side_effect = Exception("Quota exceeded")

        # Crear un archivo simulado válido
        test_image = SimpleUploadedFile(
            "test_image.jpg",
            generate_test_image(),
            content_type="image/jpeg"
        )

        response = self.client.post(
            reverse('upload_profile_photo'),
            {'photo': test_image},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Cuota de Cloudinary excedida", response.data['error'])

    @patch('userprofile.views.upload')
    def test_upload_profile_photo_no_internet(self, mock_upload):
        # Simula un error de conexión
        mock_upload.side_effect = ConnectionError("Network error")

        # Crear un archivo simulado válido
        test_image = SimpleUploadedFile(
            "test_image.jpg",
            generate_test_image(),
            content_type="image/jpeg"
        )

        response = self.client.post(
            reverse('upload_profile_photo'),
            {'photo': test_image},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("No hay conexión a Internet", response.data['error'])



##### TEST ACTUALIZACION PERFIL ####


class PatchProfileTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        # Cierra las conexiones activas para evitar problemas de eliminación
        super().tearDownClass()
        for conn in connections.all():
            conn.close()

    def setUp(self):
        # Configurar cliente API y usuario
        self.client = APIClient()
        self.user = User.objects.create_user(
            fullname="Test User",
            dni="123456789",
            email="test@example.com",
            password="Test1234!"
        )
        # Usa `get_or_create` para evitar duplicados
        self.profile, created = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                "birth_date": "1990-01-01",
                "address": "123 Test St",
                "phone_number": "123456789",
                "photo_url": "http://example.com/photo.jpg"
            }
        )
        self.client.force_authenticate(user=self.user)  # Autenticar al usuario
        self.url = reverse('patch_profile')  # Nombre de la ruta definido en urls.py

    def test_patch_profile_success(self):
        # Datos de actualización válidos
        updated_data = {
            "birth_date": "1991-02-02",
            "address": "456 New St",
            "phone_number": "987654321",
        }
        response = self.client.patch(self.url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Perfil actualizado exitosamente.")
        self.assertEqual(response.data["updated_fields"], updated_data)

        # Verificar que los datos fueron actualizados en la base de datos
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.birth_date.strftime('%Y-%m-%d'), updated_data["birth_date"])
        self.assertEqual(self.profile.address, updated_data["address"])
        self.assertEqual(self.profile.phone_number, updated_data["phone_number"])

    def test_patch_profile_no_data(self):
        # Enviar solicitud sin datos
        response = self.client.patch(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_patch_profile_invalid_field(self):
        # Intentar actualizar un campo no permitido
        invalid_data = {"invalid_field": "invalid_value"}
        response = self.client.patch(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error_invalid_field", response.data)

    def test_patch_profile_no_profile(self):
        # Eliminar el perfil del usuario antes de la prueba
        self.profile.delete()
        updated_data = {
            "address": "123 New Address"
        }

        response = self.client.patch(self.url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "El perfil no existe.")

    def test_patch_profile_unauthenticated(self):
        # Desautenticar al usuario
        self.client.force_authenticate(user=None)
        updated_data = {
            "address": "123 Unauthorized St"
        }

        response = self.client.patch(self.url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
