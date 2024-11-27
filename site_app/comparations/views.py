from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from datetime import datetime
from voltix.models import Invoice, Measurement, InvoiceComparison


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compare_invoice_and_measurement(request):
    try:
        # Obtener datos del cuerpo de la solicitud
        data = request.data
        invoice = data.get("invoice")
        measurement = data.get("measurement")

        # Validar si los datos requeridos están presentes
        if not invoice or not measurement:
            return Response({"error": "Incomplete data. 'invoice' and 'measurement' are required."}, status=400)

        # Buscar medición con las mismas fechas de inicio y fin
        measurement = Measurement.objects.filter(
            measurement_start__gte=invoice.billing_period_start,
            measurement_end__lte=invoice.billing_period_end
        ).first()


        if not measurement:
            return JsonResponse({"error": "No matching measurement found for the provided billing period."}, status=404)

        # Calcular los días facturados
        invoice_start_date = datetime.strptime(invoice.billing_period_start, "%Y-%m-%d")
        invoice_end_date = datetime.strptime(invoice.billing_period_end, "%Y-%m-%d")
        days_billed = (invoice_end_date - invoice_start_date).days + 1  # Incluye el día final

        # Detalles del consumo
        invoice_consumption = invoice.data["consumption_details"]
        measurement_consumption = measurement.data["consumption_details"]

        # Inicializamos el valor general como True
        general_match = True

        # Consumptions details: Comparar facturación y medición
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
            },
        }

        # Verificar si alguno de los `matches` es False y actualizar `general_match`
        for key, value in consumption_details.items():
            if not value["matches"]:
                general_match = False

        # Calcular el importe estimado para el consumo total (basado en medición)
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

        # Comparar `total_to_pay` entre la factura y la medición
        if invoice_consumption["total_to_pay"] != round(total_to_pay, 2):
            general_match = False

        # Crear el JSON de respuesta con los datos adicionales
        response_data = {
            "billing_period": {
                "invoice_start_date": invoice.billing_period_start,
                "invoice_end_date": invoice.billing_period_end,
                "measurement_start_date": measurement.billing_period_start,
                "measurement_end_date": measurement.billing_period_end,
                "days_billed": days_billed,
                "matches": (
                    invoice.billing_period_start == measurement.billing_period_start
                    and invoice.billing_period_end == measurement.billing_period_end
                )
            },
            "consumption_details": consumption_details,
            "total_to_pay": {
                "invoice": invoice_consumption["total_to_pay"],  # Valor tomado de la factura
                "measurement_calculation": round(total_to_pay, 2),  # Valor calculado a partir de mediciones
                "matches": invoice_consumption["total_to_pay"] == round(total_to_pay, 2)
            },
            "total_estimated_with_time_of_use": round(total_estimated_with_time_of_use, 2),
            "general_match": general_match  # Este es el nuevo valor booleano general
        }
        # Crear la instancia en InvoiceComparison
        
        InvoiceComparison.objects.create(
            user=request.user,
            invoice=invoice,
            measurement=measurement,
            comparison_results=response_data,
            is_comparison_valid=general_match
        )

        return Response(response_data, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
