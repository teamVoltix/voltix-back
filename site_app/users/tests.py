from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from voltix.models import User
from unittest.mock import patch
from datetime import datetime
from datetime import timezone

class GetAllUsersTestCase(TestCase):

    def setUp(self):
        # Crear el cliente de pruebas
        self.client = APIClient()

        # Crear usuarios de prueba
        self.user1 = User.objects.create_user(
            dni="12345678A",
            fullname="John Doe",
            email="johndoe@example.com",
            password="password123"
        )
        self.user2 = User.objects.create_user(
            dni="87654321B",
            fullname="Jane Smith",
            email="janesmith@example.com",
            password="password456"
        )

    def test_get_all_users_success(self):
    # Llamar al endpoint
        url = reverse('get_all_users')
        response = self.client.get(url)

        # Verificar que la respuesta es 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ajustar el formato de los timestamps para coincidir con el retorno del endpoint
        def format_timestamp(dt):
            return dt.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

        expected_data = {
            "message": "Usuarios obtenidos exitosamente",
            "usuarios": [
                {
                    "user_id": self.user1.id,
                    "fullname": self.user1.fullname,
                    "dni": self.user1.dni,
                    "email": self.user1.email,
                    "created_at": format_timestamp(self.user1.created_at),
                    "updated_at": format_timestamp(self.user1.updated_at),
                },
                {
                    "user_id": self.user2.id,
                    "fullname": self.user2.fullname,
                    "dni": self.user2.dni,
                    "email": self.user2.email,
                    "created_at": format_timestamp(self.user2.created_at),
                    "updated_at": format_timestamp(self.user2.updated_at),
                },
            ],
        }

        # Verificar que los datos retornados coincidan con los esperados
        self.assertDictEqual(response.json(), expected_data)
        
    
    def test_get_all_users_server_error(self):
    # Simular un error al intentar obtener los usuarios
        with patch('users.views.User.objects.all', side_effect=Exception("Simulated error")):
            url = reverse('get_all_users')
            response = self.client.get(url)

            # Verificar que el código de estado sea 500
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Verificar que el mensaje de error sea el esperado
            self.assertEqual(response.json(), {"error": "Ocurrió un error: Simulated error"})

    def test_method_not_allowed(self):
        # Intentar llamar al endpoint con un método no permitido
        url = reverse('get_all_users')
        response = self.client.post(url)  # Usando POST en lugar de GET

        # Verificar que la respuesta es 405 Method Not Allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Verificar el mensaje de error
        self.assertEqual(response.json(), {"detail": 'Method "POST" not allowed.'})
