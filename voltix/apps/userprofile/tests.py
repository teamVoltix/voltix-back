# from django.test import TestCase
# from django.urls import reverse
# from rest_framework.test import APIClient
# from rest_framework import status
# from unittest.mock import patch
# from django.core.files.uploadedfile import SimpleUploadedFile
# from apps.voltix.models import User, Profile
# from django.db import connections
# from PIL import Image
# import io
# from django.core.exceptions import ValidationError
# import json
# from django.db.models.signals import post_save
# from voltix.signals import create_user_profile, save_user_profile


# def generate_test_image():
#     """
#     Genera un archivo de imagen válido en memoria.
#     """
#     img = Image.new('RGB', (100, 100), color='red')
#     buffer = io.BytesIO()
#     img.save(buffer, format='JPEG')
#     buffer.seek(0)
#     return buffer.getvalue()


# class UploadProfilePhotoTests(TestCase):

#     @classmethod
#     def tearDownClass(cls):
#         # Cierra las conexiones activas para evitar problemas de eliminación
#         super().tearDownClass()
#         for conn in connections.all():
#             conn.close()

#     def setUp(self):
#         # Configurar cliente API y usuario
#         self.client = APIClient()
#         self.user = User.objects.create_user(
#             fullname="Test User",
#             dni="123456789",
#             email="test@example.com",
#             password="Test1234!"
#         )
#         # Usa `get_or_create` para evitar duplicados
#         self.profile, created = Profile.objects.get_or_create(
#             user=self.user,
#             defaults={"photo_url": ""}
#         )
#         self.client.force_authenticate(user=self.user)  # Autenticar al usuario

#     @patch('userprofile.views.upload')
#     def test_upload_profile_photo_success(self, mock_upload):
#         # Simula una subida exitosa
#         mock_upload.return_value = {
#             "secure_url": "https://example.com/test-photo.jpg"
#         }

#         # Crear un archivo simulado válido
#         test_image = SimpleUploadedFile(
#             "test_image.jpg",
#             generate_test_image(),
#             content_type="image/jpeg"
#         )

#         response = self.client.post(
#             reverse('upload_profile_photo'),
#             {'photo': test_image},
#             format='multipart'
#         )

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['message'], "Foto subida exitosamente.")
#         self.assertIn('photo_url', response.data)

#     def test_upload_profile_photo_no_file(self):
#         # Enviar solicitud sin archivo
#         response = self.client.post(
#             reverse('upload_profile_photo'),
#             {},
#             format='multipart'
#         )

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], "No se encontró un archivo para subir.")

#     def test_upload_profile_photo_no_profile(self):
#         # Eliminar el perfil del usuario
#         self.profile.delete()

#         # Crear un archivo simulado
#         test_image = SimpleUploadedFile(
#             "test_image.jpg",
#             generate_test_image(),
#             content_type="image/jpeg"
#         )

#         response = self.client.post(
#             reverse('upload_profile_photo'),
#             {'photo': test_image},
#             format='multipart'
#         )

#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertEqual(response.data['error'], "El perfil no existe.")

#     @patch('userprofile.views.upload')
#     def test_upload_profile_photo_cloudinary_error(self, mock_upload):
#         # Simula un error de Cloudinary
#         mock_upload.side_effect = Exception("Cloudinary error")

#         # Crear un archivo simulado válido
#         test_image = SimpleUploadedFile(
#             "test_image.jpg",
#             generate_test_image(),
#             content_type="image/jpeg"
#         )

#         response = self.client.post(
#             reverse('upload_profile_photo'),
#             {'photo': test_image},
#             format='multipart'
#         )

#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertIn("Error de Cloudinary", response.data['error'])

#     def test_upload_profile_photo_invalid_file_type(self):
#         # Crear un archivo simulado con un tipo no permitido
#         invalid_file = SimpleUploadedFile(
#             "test_file.txt",
#             b"This is a text file, not an image",
#             content_type="text/plain"
#         )

#         response = self.client.post(
#             reverse('upload_profile_photo'),
#             {'photo': invalid_file},
#             format='multipart'
#         )

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], "Tipo de archivo no válido.")

#     def test_upload_profile_photo_large_file(self):
#         # Crear un archivo simulado muy grande
#         large_file = SimpleUploadedFile(
#             "large_image.jpg",
#             b"0" * (10 * 1024 * 1024),  # 10 MB
#             content_type="image/jpeg"
#         )

#         response = self.client.post(
#             reverse('upload_profile_photo'),
#             {'photo': large_file},
#             format='multipart'
#         )

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data['error'], "El archivo excede el tamaño máximo permitido de 5 MB.")

#     def test_upload_profile_photo_unauthenticated(self):
#         # Desautenticar al usuario
#         self.client.force_authenticate(user=None)

#         # Crear un archivo simulado
#         test_image = SimpleUploadedFile(
#             "test_image.jpg",
#             generate_test_image(),
#             content_type="image/jpeg"
#         )

#         response = self.client.post(
#             reverse('upload_profile_photo'),
#             {'photo': test_image},
#             format='multipart'
#         )

#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

#     @patch('userprofile.views.upload')
#     def test_upload_profile_photo_cloudinary_quota_exceeded(self, mock_upload):
#         # Simula un error de cuota excedida
#         mock_upload.side_effect = Exception("Quota exceeded")

#         # Crear un archivo simulado válido
#         test_image = SimpleUploadedFile(
#             "test_image.jpg",
#             generate_test_image(),
#             content_type="image/jpeg"
#         )

#         response = self.client.post(
#             reverse('upload_profile_photo'),
#             {'photo': test_image},
#             format='multipart'
#         )

#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertIn("Cuota de Cloudinary excedida", response.data['error'])

#     @patch('userprofile.views.upload')
#     def test_upload_profile_photo_no_internet(self, mock_upload):
#         # Simula un error de conexión
#         mock_upload.side_effect = ConnectionError("Network error")

#         # Crear un archivo simulado válido
#         test_image = SimpleUploadedFile(
#             "test_image.jpg",
#             generate_test_image(),
#             content_type="image/jpeg"
#         )

#         response = self.client.post(
#             reverse('upload_profile_photo'),
#             {'photo': test_image},
#             format='multipart'
#         )

#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertIn("No hay conexión a Internet", response.data['error'])


# ####################################
# ##### TEST ACTUALIZACION PERFIL ####


# class PatchProfileTests(TestCase):

#     @classmethod
#     def tearDownClass(cls):
#         # Cierra las conexiones activas para evitar problemas de eliminación
#         super().tearDownClass()
#         for conn in connections.all():
#             conn.close()

#     def setUp(self):
#         # Configurar cliente API y usuario
#         self.client = APIClient()
#         self.user = User.objects.create_user(
#             fullname="Test User",
#             dni="123456789",
#             email="test@example.com",
#             password="Test1234!"
#         )
#         # Usa `get_or_create` para evitar duplicados
#         self.profile, created = Profile.objects.get_or_create(
#             user=self.user,
#             defaults={
#                 "birth_date": "1990-01-01",
#                 "address": "123 Test St",
#                 "phone_number": "123456789",
#                 "photo_url": "http://example.com/photo.jpg"
#             }
#         )
#         self.client.force_authenticate(user=self.user)  # Autenticar al usuario
#         self.url = reverse('patch_profile')  # Nombre de la ruta definido en urls.py

#     def test_patch_profile_success(self):
#         # Datos de actualización válidos
#         updated_data = {
#             "birth_date": "1991-02-02",
#             "address": "456 New St",
#             "phone_number": "987654321",
#         }
#         response = self.client.patch(self.url, updated_data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["message"], "Perfil actualizado exitosamente.")
#         self.assertEqual(response.data["updated_fields"], updated_data)

#         # Verificar que los datos fueron actualizados en la base de datos
#         self.profile.refresh_from_db()
#         self.assertEqual(self.profile.birth_date.strftime('%Y-%m-%d'), updated_data["birth_date"])
#         self.assertEqual(self.profile.address, updated_data["address"])
#         self.assertEqual(self.profile.phone_number, updated_data["phone_number"])

#     def test_patch_profile_no_data(self):
#         # Enviar solicitud sin datos
#         response = self.client.patch(self.url, {}, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)

#     def test_patch_profile_invalid_field(self):
#         # Intentar actualizar un campo no permitido
#         invalid_data = {"invalid_field": "invalid_value"}
#         response = self.client.patch(self.url, invalid_data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error_invalid_field", response.data)

#     def test_patch_profile_no_profile(self):
#         # Eliminar el perfil del usuario antes de la prueba
#         self.profile.delete()
#         updated_data = {
#             "address": "123 New Address"
#         }

#         response = self.client.patch(self.url, updated_data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertEqual(response.data["error"], "El perfil no existe.")

#     def test_patch_profile_unauthenticated(self):
#         # Desautenticar al usuario
#         self.client.force_authenticate(user=None)
#         updated_data = {
#             "address": "123 Unauthorized St"
#         }

#         response = self.client.patch(self.url, updated_data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        
        
        
#     ##########################################
#     ############ test get profile ############
    
# class ProfileViewTestCase(TestCase):

#     def setUp(self):
#         # Crear un usuario de prueba
#         self.user = User.objects.create_user(
#             dni="12345678A",
#             fullname="Test User",
#             email="testuser@example.com",
#             password="password123"
#         )
#         # Inicializar el cliente API y autenticar al usuario
#         self.client = APIClient()
#         self.client.force_authenticate(user=self.user)

#     def test_get_profile_with_existing_profile(self):
#     # Asegurarse de que el perfil existe antes de continuar
#         profile, created = Profile.objects.get_or_create(
#             user=self.user,
#             defaults={
#                 "birth_date": "1990-01-01",
#                 "address": "123 Test Street",
#                 "phone_number": "123456789",
#                 "photo_url": "http://example.com/photo.jpg"
#             }
#         )

#         # Llamar al endpoint
#         url = reverse("profile_view")
#         response = self.client.get(url)

#         # Verificar que la respuesta es 200 OK
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Verificar los datos retornados
#         expected_data = {
#             'fullname': self.user.fullname,
#             'dni': self.user.dni,
#             'email': self.user.email,
#             'birth_date': profile.birth_date,
#             'address': profile.address,
#             'phone_number': profile.phone_number,
#             'photo': profile.photo_url,
#         }
#         self.assertDictEqual(response.json(), expected_data)


#     def test_get_profile_creates_profile_if_not_exists(self):
#         # Desconectar las señales para evitar la creación automática del perfil
#         post_save.disconnect(create_user_profile, sender=User)
#         post_save.disconnect(save_user_profile, sender=User)

#         try:
#             # Asegurarse de que el perfil no exista
#             Profile.objects.filter(user=self.user).delete()
#             self.assertFalse(Profile.objects.filter(user=self.user).exists())

#             # Llamar al endpoint
#             url = reverse("profile_view")
#             response = self.client.get(url)

#             # Verificar que la respuesta es 200 OK
#             self.assertEqual(response.status_code, status.HTTP_200_OK)

#             # Verificar que el perfil fue creado automáticamente
#             self.assertTrue(Profile.objects.filter(user=self.user).exists())

#             # Verificar los datos retornados
#             profile = Profile.objects.get(user=self.user)
#             expected_data = {
#                 'fullname': self.user.fullname,
#                 'dni': self.user.dni,
#                 'email': self.user.email,
#                 'birth_date': profile.birth_date,
#                 'address': profile.address,
#                 'phone_number': profile.phone_number,
#                 'photo': profile.photo_url,
#             }
#             self.assertDictEqual(response.json(), expected_data)
#         finally:
#             # Reconectar las señales para no afectar otros tests
#             post_save.connect(create_user_profile, sender=User)
#             post_save.connect(save_user_profile, sender=User)

#     def test_get_profile_unauthenticated(self):
#         # Desautenticar al cliente
#         self.client.force_authenticate(user=None)

#         # Llamar al endpoint
#         url = reverse("profile_view")
#         response = self.client.get(url)

#         # Verificar que la respuesta es 401 Unauthorized
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)   
        
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
import os
from django.conf import settings
from apps.general.models import Profile, UploadLog

@pytest.mark.django_db
def test_upload_profile_photo():
    # Crear un usuario de prueba
    user = get_user_model().objects.create_user(
        dni="123456789",
        fullname="Test User",
        email="testuser@example.com",
        password="testpassword"
    )

    # Autenticar al usuario
    client = APIClient()
    client.force_authenticate(user=user)

    # Crear una imagen válida usando Pillow
    image = Image.new('RGB', (100, 100), color='red')  # Crear una imagen de 100x100 px roja
    image_file = io.BytesIO()  # Usar BytesIO para guardar la imagen en memoria
    image.save(image_file, format='JPEG')  # Guardar la imagen como JPEG en el archivo en memoria
    image_file.seek(0)  # Volver al inicio del archivo para leerlo

    # Convertir la imagen a un SimpleUploadedFile
    photo = SimpleUploadedFile("test_photo.jpg", image_file.read(), content_type="image/jpeg")

    # 1. Validación de los datos (se hace automáticamente al llamar el serializer)
    response = client.post('/api/profile/upload-photo/', {'photo': photo}, format='multipart')

    # Comprobar que la validación fue correcta y la respuesta es 200 OK
    assert response.status_code == status.HTTP_200_OK
    assert 'photo_url' in response.data  # Comprobamos que la URL de la foto esté en la respuesta

    # 2. Verificar que el perfil del usuario ahora tiene una foto
    profile = Profile.objects.get(user=user)
    assert profile.photo is not None, "El perfil debería tener una foto después de la subida."
    
    # Verificar que la foto se guardó correctamente en el sistema de archivos
    photo_path = os.path.join(settings.MEDIA_ROOT, profile.photo.name)
    assert os.path.exists(photo_path), f"Imagen no guardada en el sistema de archivos: {photo_path}"

    # 3. Verificar que la foto previa fue eliminada si existía
    previous_photo = None
    if profile.photo:
        previous_photo = profile.photo.name

    # 4. Subir una nueva foto
    new_image = Image.new('RGB', (100, 100), color='blue')
    new_image_file = io.BytesIO()
    new_image.save(new_image_file, format='JPEG')
    new_image_file.seek(0)

    new_photo = SimpleUploadedFile("test_new_photo.jpg", new_image_file.read(), content_type="image/jpeg")

    response = client.post('/api/profile/upload-photo/', {'photo': new_photo}, format='multipart')

    # Comprobar que la respuesta es correcta para la nueva foto
    assert response.status_code == status.HTTP_200_OK
    assert 'photo_url' in response.data  # Verificar que la URL de la nueva foto esté en la respuesta

    # 5. Verificar que la foto anterior fue eliminada
    profile.refresh_from_db()  # Recargar el perfil desde la base de datos
    assert profile.photo.name != previous_photo, "La foto anterior no ha sido eliminada correctamente."

    # Verificar que la nueva foto se guarda correctamente en el sistema de archivos
    new_photo_path = os.path.join(settings.MEDIA_ROOT, profile.photo.name)
    assert os.path.exists(new_photo_path), f"Imagen nueva no guardada en el sistema de archivos: {new_photo_path}"

    # 6. Verificar que el registro de UploadLog se ha creado
    upload_log = UploadLog.objects.filter(user=user, file_name=new_photo.name).first()
    assert upload_log is not None, "No se ha registrado la carga de la nueva foto en UploadLog."
    assert upload_log.file_name == new_photo.name, f"Se esperaba que el nombre del archivo en UploadLog fuera {new_photo.name}, pero se obtuvo {upload_log.file_name}"

    # 7. Verificar la URL proporcionada
    photo_url = response.data['photo_url']
    assert photo_url.startswith('http://') or photo_url.startswith('https://'), \
        f"Se esperaba una URL válida, pero se obtuvo: {photo_url}"
