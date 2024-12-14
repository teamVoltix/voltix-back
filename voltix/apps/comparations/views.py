from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from apps.voltix.models import Invoice, Measurement, InvoiceComparison
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(
    method="post",
    operation_summary="Compare Invoice and Measurement",
    operation_description="""
        Compares an invoice with a measurement based on billing periods and energy consumption data.

        This endpoint performs the following:
        - Validates the provided invoice ID.
        - Fetches the invoice and the corresponding measurement based on the billing period.
        - Compares consumption details and calculates the total to pay based on the measurement.
        - Stores the comparison results in the `InvoiceComparison` model.
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["invoice"],
        properties={
            "invoice": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="The ID of the invoice to compare."
            ),
        },
        example={
            "invoice": 123
        }
    ),
    responses={
        200: openapi.Response(
            description="Comparison successful.",
            examples={
                "application/json": {
                    "periodo_facturacion": {
                        "fecha_inicio_factura": "2023-01-01",
                        "fecha_fin_factura": "2023-01-31",
                        "fecha_inicio_medicion": "2023-01-01",
                        "fecha_fin_medicion": "2023-01-31",
                        "dias_facturados": 30,
                        "coincide_fechas": True
                    },
                    "detalles_consumo": {
                        "total_consumption_kwh": {
                            "invoice": 500,
                            "measurement": 495,
                            "difference": 5.0,
                            "matches": False
                        }
                    },
                    "total_a_pagar": {
                        "factura": 100.0,
                        "calculo_medicion": 98.56,
                        "coincide_total": False
                    },
                    "coincidencia_general": False
                }
            }
        ),
        400: openapi.Response(
            description="Invalid request.",
            examples={
                "application/json": {
                    "error": "'invoice' is required."
                }
            }
        ),
        404: openapi.Response(
            description="Resource not found.",
            examples={
                "application/json": {
                    "error": "Invoice not found."
                }
            }
        ),
        500: openapi.Response(
            description="Server error.",
            examples={
                "application/json": {
                    "error": "An unexpected error occurred."
                }
            }
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compare_invoice_and_measurement(request):
    try:
        data = request.data
        invoice_id = data.get("invoice")  # ID de la factura (invoice)

        # Validar si el 'invoice' está presente
        if not invoice_id:
            return Response({"error": "'invoice' is required."}, status=400)

        # Buscar el objeto Invoice
        try:
            invoice = Invoice.objects.get(id=invoice_id, user=request.user)
        except ObjectDoesNotExist:
            return Response({"error": "Invoice not found."}, status=404)

        # Buscar la medición que coincida con el período de facturación de la factura
        invoice_start_date = invoice.billing_period_start
        invoice_end_date = invoice.billing_period_end

        # Buscar mediciones que coincidan con el período de facturación
        measurements = Measurement.objects.filter(
            user=request.user,
            measurement_start__lte=invoice_end_date,
            measurement_end__gte=invoice_start_date
        )

        if not measurements.exists():
            return Response({"error": "No matching measurements found."}, status=404)

        measurement = measurements.first()
        invoice_consumption = invoice.data.get("detalles_consumo", None)
        measurement_consumption = measurement.data.get("consumo_total", None)

        if not invoice_consumption or not measurement_consumption:
            return Response({"error": "'detalles_consumo' or 'consumo_total' not found in invoice or measurement."}, status=404)

        consumo_total_invoice = invoice_consumption.get("consumo_total", 0) or 0
        consumo_total_measurement = measurement_consumption or 0

        consumption_details = {
            "total_consumption_kwh": {
                "invoice": consumo_total_invoice,
                "measurement": consumo_total_measurement,
                "difference": round(consumo_total_invoice - consumo_total_measurement, 2),
                "matches": consumo_total_invoice == consumo_total_measurement
            }
        }

        total_consumption_kWh = consumo_total_measurement
        
        # Obtener el precio por kWh de la factura
        price_per_kWh = invoice.data.get("detalles_consumo", {}).get("precio_efectivo_energia", 0.1121)

        # Verificar si el precio es válido
        if price_per_kWh <= 0:
            return Response({"error": "Invalid price_per_kWh extracted from invoice."}, status=400)

        electricity_tax_rate = 0.051127
        vat_rate = 0.21

        energy_term = total_consumption_kWh * price_per_kWh
        electricity_tax = energy_term * electricity_tax_rate
        subtotal = energy_term + electricity_tax
        vat = subtotal * vat_rate
        total_to_pay = subtotal + vat

        total_a_pagar = invoice.data.get("desglose_cargos", {}).get("total_a_pagar", 0)
        total_to_pay_matches = total_a_pagar == round(total_to_pay, 2)
        dates_match = invoice_start_date == measurement.measurement_start.date() and invoice_end_date == measurement.measurement_end.date()

        response_data = {
            "periodo_facturacion": {
                "fecha_inicio_factura": invoice_start_date.strftime('%Y-%m-%d'),
                "fecha_fin_factura": invoice_end_date.strftime('%Y-%m-%d'),
                "fecha_inicio_medicion": measurement.measurement_start.strftime('%Y-%m-%d'),
                "fecha_fin_medicion": measurement.measurement_end.strftime('%Y-%m-%d'),
                "dias_facturados": invoice.data.get("periodo_facturacion", {}).get("dias", 0),
                "coincide_fechas": dates_match
            },
            "detalles_consumo": consumption_details,
            "total_a_pagar": {
                "factura": total_a_pagar,
                "calculo_medicion": round(total_to_pay, 2),
                "coincide_total": total_to_pay_matches
            },
            "coincidencia_general": all(value["matches"] for value in consumption_details.values()) and total_to_pay_matches and dates_match
        }

        comparison = InvoiceComparison.objects.create(
            user=request.user,
            invoice=invoice,
            measurement=measurement,
            comparison_results=response_data,
            is_comparison_valid=response_data["coincidencia_general"]       
        )
        
        response = {
            "status": "success",
            "message": "Comparison completed successfully.",
            "user_id": request.user.id,
            "invoice_id": invoice.id,
            "measurement_id": measurement.id,
            "invoice_created_at": invoice.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "measurement_created_at": measurement.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "comparison_id": comparison.id,
            "result": response_data
        }

        return Response(response, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
