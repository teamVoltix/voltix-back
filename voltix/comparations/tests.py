from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from voltix.models import User, Invoice, Measurement, InvoiceComparison
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
import json


class CompareInvoiceAndMeasurementTest(APITestCase):

    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create(
            dni='12345678X',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.invoice = Invoice.objects.create(
            user=self.user,
            billing_period_start=datetime(2023, 1, 1),
            billing_period_end=datetime(2023, 1, 31),
            data={
                "detalles_consumo": {"consumo_total": 500},
                "desglose_cargos": {"total_a_pagar": 100.0}
            }
        )

        self.measurement = Measurement.objects.create(
            user=self.user,
            measurement_start=timezone.make_aware(datetime(2023, 1, 1)),
            measurement_end=timezone.make_aware(datetime(2023, 1, 31)),
            data={"consumo_total": 495}
        )

        self.compare_url = '/comparations/compare/'

    def test_compare_invoice_and_measurement_success(self):
        """Test para comparación exitosa"""
        payload = {"invoice": self.invoice.id}
        response = self.client.post(self.compare_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json() 
        self.assertIn("result", response_data)
        self.assertEqual(response_data["result"]["coincidencia_general"], False)

    def test_compare_invoice_not_found(self):
        """Test para error de factura no encontrada"""
        payload = {"invoice": 9999}  # ID inexistente
        response = self.client.post(self.compare_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        try:
            response_data = response.json()  # Convierte la respuesta a JSON
            self.assertIn("error", response_data)
        except ValueError:
            print(response.content)

    def test_compare_missing_invoice_param(self):
        """Test para parámetro de factura faltante"""
        payload = {}
        response = self.client.post(self.compare_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn("error", response_data)

    def test_user_comparison_list_view(self):
        """Test para listar comparaciones del usuario"""
        comparison = InvoiceComparison.objects.create(
            user=self.user,
            invoice=self.invoice,
            measurement=self.measurement,
            comparison_results={"coincidencia_general": True},
            is_comparison_valid=True
        )
        response = self.client.get('/comparations/comparisons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]["invoice_id"], self.invoice.id)

    def test_user_comparison_detail_view(self):
        """Test para detalle de una comparación"""
        comparison = InvoiceComparison.objects.create(
            user=self.user,
            invoice=self.invoice,
            measurement=self.measurement,
            comparison_results={"coincidencia_general": True},
            is_comparison_valid=True
        )
        response = self.client.get(f'/comparations/comparisons/{comparison.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["invoice_id"], self.invoice.id)

    def test_user_comparison_detail_not_found(self):
        """Test para comparación no encontrada"""
        response = self.client.get('/comparisons/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        try:
            response_data = response.json()
            self.assertIn("error", response_data)
        except ValueError:
            print(response.content)
    def test_compare_invoice_extreme_values(self):
        """Test para valores extremos en la comparación"""
        self.invoice.data = {"detalles_consumo": {"consumo_total": 999999}}
        self.invoice.save()
        payload = {"invoice": self.invoice.id}
        response = self.client.post(self.compare_url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["result"]["coincidencia_general"], False)
    def test_invalid_invoice_dates(self):
        """Test para fechas inválidas en la factura"""
        invoice = Invoice(
            user=self.user,  # Asegúrate de usar 'user', no 'User'
            billing_period_start=datetime(2023, 2, 1),
            billing_period_end=datetime(2023, 1, 31),  # Fecha de inicio posterior al fin
            data={"detalles_consumo": {"consumo_total": 300}}
        )
        with self.assertRaises(ValidationError):  # Cambiado a ValidationError
            invoice.full_clean()  # Lanza error por fechas inválidas
