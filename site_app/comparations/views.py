from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from voltix.models import Invoice, Measurement, InvoiceComparison


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compare_invoice_and_measurement(request):
    try:
        # Obtener datos del cuerpo de la solicitud
        data = request.data
        invoice_id = data.get("invoice")  # ID de la factura (invoice)
        
        # Validar si el 'invoice' está presente
        if not invoice_id:
            return Response({"error": "'invoice' is required."}, status=400)

        # Buscar el objeto Invoice
        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Invoice not found."}, status=404)

        # Buscar la medición que coincida con el período de facturación de la factura
        invoice_start_date = datetime.strptime(invoice.billing_period_start, "%Y-%m-%d")
        invoice_end_date = datetime.strptime(invoice.billing_period_end, "%Y-%m-%d")

        # Buscar mediciones que coincidan con el período de facturación
        measurements = Measurement.objects.filter(
            measurement_start__lte=invoice_end_date,
            measurement_end__gte=invoice_start_date
        )
        
        # Si no se encuentra ninguna medición que coincida con las fechas, retornar un error
        if not measurements.exists():
            return JsonResponse({"error": "No matching measurements found."}, status=404)

        # Supongamos que hay solo una medición que coincide. Si hay más, debes decidir cómo manejarlas.
        measurement = measurements.first()

        # Comparar las fechas de la factura y medición
        measurement_start_date = datetime.strptime(measurement.measurement_start, "%Y-%m-%d")
        measurement_end_date = datetime.strptime(measurement.measurement_end, "%Y-%m-%d")

        days_billed = (invoice_end_date - invoice_start_date).days + 1  # Incluye el día final

        # Verificar si las fechas coinciden
        dates_match = (
            invoice.billing_period_start == measurement.measurement_start and
            invoice.billing_period_end == measurement.measurement_end
        )

        # Detalles del consumo
        invoice_consumption = invoice.data["consumption_details"]
        measurement_consumption = measurement.data["consumption_details"]

        # Comparar los detalles de consumo
        consumption_details = {
            "total_consumption_kwh": {
                "invoice": invoice_consumption["total_consumption"],
                "measurement": measurement_consumption["total_consumption"],
                "difference": round(invoice_consumption["total_consumption"] - measurement_consumption["total_consumption"], 2),
                "matches": invoice_consumption["total_consumption"] == measurement_consumption["total_consumption"]
            },
            "peak_consumption": {
                "invoice": invoice_consumption["peak_consumption"],
                "measurement": measurement_consumption["peak_consumption"],
                "difference": round(invoice_consumption["peak_consumption"] - measurement_consumption["peak_consumption"], 2),
                "matches": invoice_consumption["peak_consumption"] == measurement_consumption["peak_consumption"]
            },
            "off_peak_consumption": {
                "invoice": invoice_consumption["off_peak_consumption"],
                "measurement": measurement_consumption["off_peak_consumption"],
                "difference": round(invoice_consumption["off_peak_consumption"] - measurement_consumption["off_peak_consumption"], 2),
                "matches": invoice_consumption["off_peak_consumption"] == measurement_consumption["off_peak_consumption"]
            }
        }

        # Calcular el importe total estimado para el consumo total (basado en medición)
        total_consumption_kWh = measurement_consumption["total_consumption"]
        price_per_kWh = 0.1121  # Precio por kWh
        electricity_tax_rate = 0.051127  # Tasa del impuesto sobre la electricidad
        vat_rate = 0.21  # IVA al 21%

        energy_term = total_consumption_kWh * price_per_kWh
        electricity_tax = energy_term * electricity_tax_rate
        subtotal = energy_term + electricity_tax
        vat = subtotal * vat_rate
        total_to_pay = subtotal + vat

        # Si hay discriminación horaria, calcular el total estimado para cada franja horaria
        if "peak_consumption" in measurement_consumption and "off_peak_consumption" in measurement_consumption:
            peak_price = 0.15
            off_peak_price = 0.10
            peak_consumption_kWh = measurement_consumption["peak_consumption"]
            off_peak_consumption_kWh = measurement_consumption["off_peak_consumption"]

            peak_energy_term = peak_consumption_kWh * peak_price
            off_peak_energy_term = off_peak_consumption_kWh * off_peak_price
            total_energy_term = peak_energy_term + off_peak_energy_term

            total_electricity_tax = total_energy_term * electricity_tax_rate
            total_subtotal = total_energy_term + total_electricity_tax
            total_vat = total_subtotal * vat_rate
            total_estimated_with_time_of_use = total_subtotal + total_vat
        else:
            total_estimated_with_time_of_use = total_to_pay

        # Comparar el total a pagar entre la factura y la medición
        total_to_pay_matches = invoice_consumption["total_to_pay"] == round(total_to_pay, 2)

        # Crear el JSON de respuesta con los datos adicionales
        response_data = {
            "billing_period": {
                "invoice_start_date": invoice.billing_period_start,
                "invoice_end_date": invoice.billing_period_end,
                "measurement_start_date": measurement.measurement_start, 
                "measurement_end_date": measurement.measurement_end, 
                "days_billed": days_billed,
                "matches": dates_match
            },
            "consumption_details": consumption_details,
            "total_to_pay": {
                "invoice": invoice_consumption["total_to_pay"],  # Valor tomado de la factura
                "measurement_calculation": round(total_to_pay, 2),  # Valor calculado a partir de mediciones
                "matches": total_to_pay_matches
            },
            "total_estimated_with_time_of_use": round(total_estimated_with_time_of_use, 2),
            "general_match": all(value["matches"] for value in consumption_details.values()) and total_to_pay_matches and dates_match
        }

        # Crear la instancia en InvoiceComparison
        InvoiceComparison.objects.create(
            user=request.user,
            invoice=invoice,
            measurement=measurement,
            comparison_results=response_data,
            is_comparison_valid=response_data["general_match"]
        )

        return Response(response_data, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
