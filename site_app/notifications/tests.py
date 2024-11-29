from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from voltix.models import User, NotificationSettings
from notifications.serializers import NotificationSettingsSerializer  # Ajusta si es necesario

class NotificationSettingsViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            dni="123456789",
            fullname="Test User",
            email="testuser@example.com",
            password="password123"
        )
        self.client.force_authenticate(user=self.user)
        self.url = "/api/notifications/settings/"  # Ajusta esta URL según tu configuración

    def test_create_new_notification_settings(self):
        data = {
            "enable_alerts": True,
            "enable_recommendations": False,
            "enable_reminders": True,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data["status"], "success")
        self.assertEqual(NotificationSettings.objects.filter(user=self.user).count(), 1)

    def test_update_notification_settings_successfully(self):
        NotificationSettings.objects.create(user=self.user)
        data = {
            "enable_alerts": False,
            "enable_recommendations": True,
            "enable_reminders": True,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        settings = NotificationSettings.objects.get(user=self.user)
        self.assertEqual(settings.enable_alerts, False)
        self.assertEqual(settings.enable_recommendations, True)
        self.assertEqual(settings.enable_reminders, True)

    def test_invalid_payload(self):
        data = {"invalid_field": True}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")

    def test_partial_update_notification_settings(self):
        NotificationSettings.objects.create(user=self.user)
        data = {"enable_alerts": False}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        settings = NotificationSettings.objects.get(user=self.user)
        self.assertEqual(settings.enable_alerts, False)
        self.assertEqual(settings.enable_recommendations, True)  # Default value
        self.assertEqual(settings.enable_reminders, True)  # Default value

    def test_field_limitations(self):
        data = {
            "enable_alerts": True,
            "enable_recommendations": True,
            "enable_reminders": True,
            "extra_field": True,  # This field should not be allowed
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")

    def test_invalid_data_type(self):
        data = {"enable_alerts": "not_a_boolean"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")
