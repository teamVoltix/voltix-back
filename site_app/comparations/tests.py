from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from voltix.models import Invoice, Measurement, InvoiceComparison, User
from datetime import date

class CompareInvoiceAndMeasurementTest(APITestCase):

    def setUp(self):
        """Método para configurar el entorno de pruebas"""
        # Crear un usuario
        self.user = User.objects.create_user(
            
            dni='12345678X',           # Añadir un DNI de ejemplo
            password='testpassword',
            fullname='Test User',       # Añadir un nombre completo de ejemplo
            email='testuser@example.com'  # Añadir un correo electrónico de ejemplo
        )

        # Crear una factura de ejemplo
        self.invoice = Invoice.objects.create(
            user=self.user,
            billing_period_start=date(2023, 11, 1),
            billing_period_end=date(2023, 11, 30),
            data={
                "detalles_consumo": {
                    "consumo_total": 340.0
                },
                "desglose_cargos": {
                    "total_a_pagar": 460.0
                }
            }
        )

        # Crear una medición de ejemplo
        self.measurement = Measurement.objects.create(
            user=self.user,
            measurement_start=date(2023, 11, 1),
            measurement_end=date(2023, 11, 30),
            data={"consumo_total": 245.0}
        )

        # Obtener el token de autenticación para el usuario (si es necesario)
        self.client.login(username='testuser', password='testpassword')

    def test_compare_invoice_and_measurement(self):
        """Probar la vista compare_invoice_and_measurement"""
        url = '/comparisons/'  # Asegúrate de usar la URL correcta
        data = {
            "invoice": self.invoice.id  # Enviar la ID de la factura para comparar
        }

        # Realizar la solicitud POST
        response = self.client.post(url, data, format='json')

        # Verificar que el código de estado sea 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que los resultados de la comparación estén en la respuesta
        response_data = response.json()
        self.assertIn("status", response_data)
        self.assertIn("result", response_data)
        self.assertEqual(response_data["status"], "success")

        # Verificar la coincidencia de los consumos (esto se puede ajustar según el comportamiento esperado)
        consumo_factura = self.invoice.data["detalles_consumo"]["consumo_total"]
        consumo_medicion = self.measurement.data["consumo_total"]
        self.assertEqual(consumo_factura, consumo_medicion)  # O puedes comparar si hay alguna diferencia

        # Verificar que la comparación fue guardada en la base de datos
        comparison = InvoiceComparison.objects.get(id=response_data["comparison_id"])
        self.assertEqual(comparison.invoice.id, self.invoice.id)
        self.assertEqual(comparison.measurement.id, self.measurement.id)

    def test_missing_invoice(self):
        """Probar si falta la factura en la solicitud"""
        url = '/comparisons/'
        data = {}  # No enviar la factura

        response = self.client.post(url, data, format='json')

        # Verificar que la respuesta tenga un error 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_invoice_not_found(self):
        """Probar si la factura no se encuentra"""
        url = '/comparisons/'
        data = {
            "invoice": 9999  # ID de factura que no existe
        }

        response = self.client.post(url, data, format='json')

        # Verificar que la respuesta tenga un error 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.json())
