from django.contrib.contenttypes.models import ContentType
from rest_framework_simplejwt.tokens import RefreshToken
from voltix.models import Notification
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

class NotificationTests(APITestCase):
    def setUp(self):
        # Crear un usuario para probar los endpoints
        self.user = get_user_model().objects.create_user(
            dni="7782452J",
            fullname="John Smith",
            email="john.smith@outlook.com",
            password="Secur3John@"
        )
        
        # Obtener el ContentType para un modelo relacionado, por ejemplo, un modelo llamado `SomeModel`
        # Reemplaza `SomeModel` con el modelo que quieras usar para el object_id
        content_type = ContentType.objects.get_for_model(Notification)

        # Crear algunas notificaciones para este usuario
        self.notification1 = Notification.objects.create(
            user=self.user,
            message="Alerta importante",
            type="alerta",
            created_at=timezone.now(),
            content_type=content_type,
            object_id=12  # Reemplaza con un ID válido de tu modelo relacionado
        )
        
        self.notification2 = Notification.objects.create(
            user=self.user,
            message="Recomendación sobre seguridad",
            type="recomendacion",
            created_at=timezone.now() - timezone.timedelta(days=5),
            content_type=content_type,
            object_id=12  # Reemplaza con un ID válido de tu modelo relacionado
        )
        
        self.notification3 = Notification.objects.create(
            user=self.user,
            message="Recordatorio de cita médica",
            type="recordatorio",
            created_at=timezone.now() - timezone.timedelta(days=10),
            content_type=content_type,
            object_id=13  # Reemplaza con un ID válido de tu modelo relacionado
        )
        
        # Obtener JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def get_authentication_headers(self):
        # Retornar los headers necesarios con el token de autenticación
        return {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}  # Cambié el prefijo a 'HTTP_' para que funcione correctamente en pruebas

    def test_get_all_notifications(self):
        # Test para obtener todas las notificaciones de un usuario
        response = self.client.get('/api/notifications/', **self.get_authentication_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # Debe devolver las 3 notificaciones

    def test_get_notifications_by_date_range(self):
        # Test para obtener notificaciones dentro de un rango de fechas
        start_date = '2024-11-01'
        end_date = '2024-11-29'
        response = self.client.get(f'/api/notifications/?start_date={start_date}&end_date={end_date}', 
                                   **self.get_authentication_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Debe devolver 2 notificaciones (dentro de ese rango)

    def test_get_notifications_by_type(self):
        # Test para obtener notificaciones por tipo
        response = self.client.get('/api/notifications/?type=alerta', 
                                   **self.get_authentication_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Debe devolver solo 1 notificación de tipo 'alerta'
        self.assertEqual(response.data[0]['type'], 'alerta')  # Verifica que sea del tipo 'alerta'

    def test_get_notifications_no_auth(self):
        # Test para intentar acceder sin estar autenticado (sin enviar el token JWT)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # Debe devolver 401 Unauthorized
