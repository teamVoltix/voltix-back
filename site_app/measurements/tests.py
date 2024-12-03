from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from voltix.models import User, Measurement
from datetime import datetime, timedelta


class MeasurementViewTests(TestCase):
    def setUp(self):
        # Crear un cliente de API y un usuario de prueba
        self.client = APIClient()
        self.user = User.objects.create_user(
            dni="987654321",
            fullname="Measurement User",
            email="measureuser@example.com",
            password="password123"
        )
        self.client.force_authenticate(user=self.user)  # Autenticar al usuario
        self.url = "/api/measurements/"  # URL de la API que vamos a probar

    def test_create_measurement_successfully(self):
        # Datos de la medición a enviar
        data = {
            "measurement_start": datetime.now().isoformat(),
            "measurement_end": (datetime.now() + timedelta(hours=1)).isoformat(),
            "data": {
                "consumo_total": 100,
                "tension_promedio": 220
            }
        }
        # Enviar la solicitud POST
        response = self.client.post(self.url, data, format="json")
        # Comprobar que la respuesta es correcta
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Measurement.objects.count(), 1)
        measurement = Measurement.objects.first()
        self.assertEqual(measurement.data["consumo_total"], 100)

    def test_update_measurement_successfully(self):
        # Crear una medición de prueba
        measurement = Measurement.objects.create(
            user=self.user,
            measurement_start=datetime.now(),
            measurement_end=datetime.now() + timedelta(hours=1),
            data={"consumo_total": 100}
        )
        update_url = f"{self.url}{measurement.id}/"
        data = {
            "data": {
                "consumo_total": 150,
                "tension_promedio": 230
            }
        }
        # Enviar solicitud PUT para actualizar
        response = self.client.put(update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_measurement = Measurement.objects.get(id=measurement.id)
        self.assertEqual(updated_measurement.data["consumo_total"], 150)

    def test_get_all_measurements(self):
        # Crear una medición de prueba
        Measurement.objects.create(
            user=self.user,
            measurement_start=datetime.now(),
            measurement_end=datetime.now() + timedelta(hours=1),
            data={"consumo_total": 100}
        )
        # Enviar solicitud GET para obtener todas las mediciones
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["measurements"]), 1)

    def test_get_single_measurement(self):
        # Crear una medición de prueba
        measurement = Measurement.objects.create(
            user=self.user,
            measurement_start=datetime.now(),
            measurement_end=datetime.now() + timedelta(hours=1),
            data={"consumo_total": 100}
        )
        # Enviar solicitud GET para obtener una medición específica
        response = self.client.get(f"{self.url}{measurement.id}/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["consumo_total"], 100)

    def test_invalid_measurement_creation(self):
        # Enviar datos inválidos
        data = {
            "measurement_start": "invalid_date",
            "measurement_end": "invalid_date",
            "data": {"consumo_total": "not_a_number"}
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_measurement_successfully(self):
        # Crear una medición de prueba
        measurement = Measurement.objects.create(
            user=self.user,
            measurement_start=datetime.now(),
            measurement_end=datetime.now() + timedelta(hours=1),
            data={"consumo_total": 100}
        )
        delete_url = f"{self.url}{measurement.id}/"
        # Enviar solicitud DELETE
        response = self.client.delete(delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Measurement.objects.count(), 0)
