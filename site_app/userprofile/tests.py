from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from voltix.models import User, Profile
from django.db import connections  # Importar conexiones

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

    @patch('userprofile.views.upload')  # Mock de la función `upload` de Cloudinary
    def test_upload_profile_photo_success(self, mock_upload):
        # Configurar el mock para simular una subida exitosa
        mock_upload.return_value = {
            "secure_url": "https://example.com/test-photo.jpg"
        }

        # Crear un archivo simulado
        test_image = SimpleUploadedFile(
            "test_image.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )

        response = self.client.post(
            reverse('upload_profile_photo'),  # Nombre de la URL para el endpoint
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
            b"fake_image_content",
            content_type="image/jpeg"
        )

        response = self.client.post(
            reverse('upload_profile_photo'),
            {'photo': test_image},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "El perfil no existe.")

    @patch('userprofile.views.upload')  # Mock de la función `upload` de Cloudinary
    def test_upload_profile_photo_cloudinary_error(self, mock_upload):
        # Configurar el mock para simular un error de Cloudinary
        mock_upload.side_effect = Exception("Cloudinary error")

        # Crear un archivo simulado
        test_image = SimpleUploadedFile(
            "test_image.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )

        response = self.client.post(
            reverse('upload_profile_photo'),
            {'photo': test_image},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Cloudinary", response.data['error'])

