from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from voltix.models import Measurement, User
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

class MeasurementTests(TestCase):
    """
    Pruebas para las funcionalidades de mediciones.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            dni="987654321", fullname="Test User", email="testuser@example.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.base_url = reverse("get_all_measurements")
        self.detail_url = lambda measurement_id: reverse("measurement_detail", args=[measurement_id])

        # Crear una medición para la prueba de detalle
        # Convertimos las fechas a objetos timezone-aware utilizando make_aware para evitar errores con fechas naive.
        self.measurement = Measurement.objects.create(
            user=self.user,
            measurement_start=make_aware(datetime.now()),
            measurement_end=make_aware(datetime.now() + timedelta(hours=1)),
            data={"consumo_total": 100, "tension_promedio": 220}
        )
        """
        Explicación:
        Django requiere que los campos DateTimeField trabajen con fechas *timezone-aware* cuando el soporte para zonas horarias está habilitado (USE_TZ=True).
        `datetime.now()` devuelve un objeto *naive* que no tiene información de zona horaria. 
        Usamos `make_aware` para convertir estas fechas a objetos *timezone-aware*, asegurando compatibilidad con el sistema de tiempo de Django.
        """

    def test_get_all_measurements(self):
        """
        Probar que se pueden obtener todas las mediciones del sistema.
        """
        response = self.client.get(self.base_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("measurements", response.data)
        self.assertEqual(len(response.data["measurements"]), 1)

    def test_get_measurement_detail(self):
        """
        Probar que un usuario autenticado puede obtener el detalle de una medición específica.
        """
        response = self.client.get(self.detail_url(self.measurement.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.measurement.id)
        self.assertEqual(response.data["data"]["consumo_total"], 100)

    def test_unauthorized_access_to_detail(self):
        """
        Probar que un usuario no autenticado no puede acceder al detalle de una medición.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(self.detail_url(self.measurement.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


"""
Expliación de los tests:

- test_get_all_measurements: Verifica el acceso al endpoint abierto para obtener todas las mediciones.

- test_get_measurement_detail: Probar el acceso al detalle de una medición para usuarios autenticados.

- test_unauthorized_access_to_detail: Verifica que el detalle de mediciones requiera autenticación.

- Para ver los tests ejecutar: 

python site_app/manage.py test measurements.tests --keepdb

- Para ve los tests con más detalle:

python site_app/manage.py test measurements.tests --keepdb -v 2

"""