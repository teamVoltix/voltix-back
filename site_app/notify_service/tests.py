from unittest import mock
from django.test import TestCase
from rest_framework.test import APIClient
from voltix.models import Notification
from datetime import datetime

class NotificationListViewTest(TestCase):
    def setUp(self):
        # Inicializa el cliente de API
        self.client = APIClient()
        self.client.force_authenticate(user=self.create_user())  # Autenticar un usuario para la prueba

    def create_user(self):
        # Crea un usuario de prueba
        from django.contrib.auth.models import User
        return User.objects.create_user(username="testuser", password="testpass")

    @mock.patch('voltix.models.Notification.objects.filter')
    def test_get_notifications(self, mock_filter):
        # Simulamos el comportamiento de get_queryset() para devolver notificaciones
        mock_filter.return_value = [
            Notification(id=1, message='Test Notification 1', user=self.create_user()),
            Notification(id=2, message='Test Notification 2', user=self.create_user())
        ]
        
        # Realizamos la petición GET al endpoint
        response = self.client.get('/api/notifications/')
        
        # Verificamos que la respuesta es correcta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['message'], 'Test Notification 1')
        self.assertEqual(response.data[1]['message'], 'Test Notification 2')

    @mock.patch('voltix.models.Notification.objects.filter')
    def test_get_notifications_by_type(self, mock_filter):
        # Simulamos el comportamiento de get_queryset() para devolver notificaciones de tipo 'alerta'
        mock_filter.return_value = [
            Notification(id=1, message='Alert Notification', user=self.create_user(), type='alerta')
        ]
        
        # Realizamos la petición GET con un parámetro de tipo
        response = self.client.get('/api/notifications/?type=alerta')
        
        # Verificamos que la respuesta es correcta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], 'Alert Notification')

    @mock.patch('voltix.models.Notification.objects.filter')
    def test_get_notifications_by_date(self, mock_filter):
        # Simulamos el comportamiento de get_queryset() para devolver notificaciones en una fecha específica
        mock_filter.return_value = [
            Notification(id=1, message='Notification on specific date', user=self.create_user(), created_at='2024-01-01')
        ]
        
        # Realizamos la petición GET con un parámetro de fecha
        response = self.client.get('/api/notifications/?start_date=2024-01-01')
        
        # Verificamos que la respuesta es correcta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], 'Notification on specific date')

    @mock.patch('voltix.models.Notification.objects.filter')
    def test_get_notifications_by_date_range(self, mock_filter):
        # Simulamos el comportamiento de get_queryset() para devolver notificaciones dentro de un rango de fechas
        mock_filter.return_value = [
            Notification(id=1, message='Notification in date range', user=self.create_user(), created_at='2024-01-01')
        ]
        
        # Realizamos la petición GET con un parámetro de fecha de inicio y final
        response = self.client.get('/api/notifications/?start_date=2024-01-01&end_date=2024-12-31')
        
        # Verificamos que la respuesta es correcta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], 'Notification in date range')

    @mock.patch('voltix.models.Notification.objects.filter')
    def test_get_notifications_no_data(self, mock_filter):
        # Simulamos el caso en que no hay notificaciones
        mock_filter.return_value = []
        
        # Realizamos la petición GET
        response = self.client.get('/api/notifications/')
        
        # Verificamos que la respuesta es correcta, pero sin datos
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

# ------------------------------------------------------------

class NotificationListViewTestRealDB(TestCase):
    def setUp(self):
        # Inicializa el cliente de API y crea un usuario
        self.client = APIClient()
        self.user = self.create_user()
        self.client.force_authenticate(user=self.user)

        # Crea algunas notificaciones en la base de datos real
        Notification.objects.create(message="Test Notification 1", user=self.user)
        Notification.objects.create(message="Test Notification 2", user=self.user, type="alerta")
        Notification.objects.create(message="Test Notification 3", user=self.user, created_at="2024-01-01")

    def create_user(self):
        # Crea un usuario de prueba
        from django.contrib.auth.models import User
        return User.objects.create_user(username="testuser", password="testpass")

    def test_get_notifications(self):
        # Realiza la petición GET al endpoint
        response = self.client.get('/api/notifications/')
        
        # Verifica la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

    def test_get_notifications_by_type(self):
        # Realiza la petición GET con un parámetro de tipo
        response = self.client.get('/api/notifications/?type=alerta')
        
        # Verifica la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_notifications_by_date(self):
        # Realiza la petición GET con un parámetro de fecha
        response = self.client.get('/api/notifications/?start_date=2024-01-01')
        
        # Verifica la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_notifications_by_date_range(self):
        # Realiza la petición GET con un rango de fechas
        response = self.client.get('/api/notifications/?start_date=2024-01-01&end_date=2024-12-31')
        
        # Verifica la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_notifications_no_data(self):
        # Borra todas las notificaciones
        Notification.objects.all().delete()
        
        # Realiza la petición GET
        response = self.client.get('/api/notifications/')
        
        # Verifica que no hay notificaciones
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
