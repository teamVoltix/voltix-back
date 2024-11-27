from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
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
        invoice_start_date = invoice.billing_period_start  # Es de tipo datetime.date
        invoice_end_date = invoice.billing_period_end  # Es de tipo datetime.date

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

        # Verificar si existen los detalles de consumo en los datos de la factura y medición
        invoice_consumption = invoice.data.get("detalles_consumo", None)
        measurement_consumption = measurement.data.get("consumo_por_franja_horaria", None)

        # Si no se encuentran los detalles de consumo en la factura o medición, retornar un error
        if not invoice_consumption or not measurement_consumption:
            return JsonResponse({"error": "'detalles_consumo' not found in invoice or measurement."}, status=404)

        # Asegurarse de que no haya valores None, reemplazarlos con 0
        consumo_total_invoice = invoice_consumption.get("consumo_total", 0) or 0
        consumo_punta_invoice = invoice_consumption.get("consumo_punta", 0) or 0
        consumo_valle_invoice = invoice_consumption.get("consumo_valle", 0) or 0
        
        consumo_total_measurement = measurement_consumption.get("consumo_total", 0) or 0
        consumo_punta_measurement = measurement_consumption.get("punta", 0) or 0
        consumo_valle_measurement = measurement_consumption.get("valle", 0) or 0

        # Detalles del consumo
        consumption_details = {
            "total_consumption_kwh": {
                "invoice": consumo_total_invoice,
                "measurement": consumo_total_measurement,
                "difference": round(consumo_total_invoice - consumo_total_measurement, 2),
                "matches": consumo_total_invoice == consumo_total_measurement
            },
            "peak_consumption": {
                "invoice": consumo_punta_invoice,
                "measurement": consumo_punta_measurement,
                "difference": round(consumo_punta_invoice - consumo_punta_measurement, 2),
                "matches": consumo_punta_invoice == consumo_punta_measurement
            },
            "off_peak_consumption": {
                "invoice": consumo_valle_invoice,
                "measurement": consumo_valle_measurement,
                "difference": round(consumo_valle_invoice - consumo_valle_measurement, 2),
                "matches": consumo_valle_invoice == consumo_valle_measurement
            }
        }

        # Calcular el importe total estimado para el consumo total (basado en medición)
        total_consumption_kWh = consumo_total_measurement
        price_per_kWh = 0.1121  # Precio por kWh
        electricity_tax_rate = 0.051127  # Tasa del impuesto sobre la electricidad
        vat_rate = 0.21  # IVA al 21%

        energy_term = total_consumption_kWh * price_per_kWh
        electricity_tax = energy_term * electricity_tax_rate
        subtotal = energy_term + electricity_tax
        vat = subtotal * vat_rate
        total_to_pay = subtotal + vat

        # Si hay discriminación horaria, calcular el total estimado para cada franja horaria
        if "punta" in measurement_consumption and "valle" in measurement_consumption:
            peak_price = 0.15
            off_peak_price = 0.10
            peak_consumption_kWh = consumo_punta_measurement
            off_peak_consumption_kWh = consumo_valle_measurement

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
        total_to_pay_matches = invoice_consumption.get("desglose_cargos", {}).get("total_a_pagar", 0) == round(total_to_pay, 2)

        # Comparar las fechas (para 'dates_match')
        dates_match = invoice_start_date == measurement.measurement_start and invoice_end_date == measurement.measurement_end

        # Crear el JSON de respuesta con los datos adicionales
        response_data = {
            "billing_period": {
                "invoice_start_date": invoice.billing_period_start.strftime('%Y-%m-%d'),  # Convertir a string
                "invoice_end_date": invoice.billing_period_end.strftime('%Y-%m-%d'),  # Convertir a string
                "measurement_start_date": measurement.measurement_start.strftime('%Y-%m-%d'),  # Convertir a string
                "measurement_end_date": measurement.measurement_end.strftime('%Y-%m-%d'),  # Convertir a string
                "days_billed": (invoice_end_date - invoice_start_date).days + 1,
                "matches": dates_match
            },
            "consumption_details": consumption_details,
            "total_to_pay": {
                "invoice": invoice_consumption.get("desglose_cargos", {}).get("total_a_pagar", 0),  # Valor tomado de la factura
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
