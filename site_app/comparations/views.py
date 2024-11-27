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
        measurement_id = data.get("measurement")  # ID de la medición (measurement)

        # Validar si se proporcionan al menos uno de los IDs
        if not invoice_id and not measurement_id:
            return Response({"error": "'invoice' or 'measurement' is required."}, status=400)

        invoice = None
        measurement = None
        invoice_start_date = None
        invoice_end_date = None

        if invoice_id:
            # Buscar el objeto Invoice
            try:
                invoice = Invoice.objects.get(id=invoice_id)
                invoice_start_date = invoice.billing_period_start
                invoice_end_date = invoice.billing_period_end
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Invoice not found."}, status=404)

        if measurement_id:
            # Buscar la medición con el ID proporcionado
            try:
                measurement = Measurement.objects.get(id=measurement_id)
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Measurement not found."}, status=404)

        if invoice:
            # Verificar si las fechas de la factura son válidas antes de usarlas
            if invoice_start_date and invoice_end_date:
                # Buscar la medición que coincida con el período de facturación de la factura
                measurements = Measurement.objects.filter(
                    measurement_start__lte=invoice_end_date,
                    measurement_end__gte=invoice_start_date
                )

                # Si no se encuentra ninguna medición que coincida con las fechas, retornar un error
                if not measurements.exists():
                    return JsonResponse({"error": "No matching measurements found."}, status=404)

                # Supongamos que hay solo una medición que coincide. Si hay más, debes decidir cómo manejarlas.
                measurement = measurements.first()

        elif measurement:
            # Verificar si las fechas de la medición son válidas antes de usarlas
            if measurement.measurement_start and measurement.measurement_end:
                # Buscar la factura que coincida con el período de medición de la medición
                measurement_start_date = measurement.measurement_start
                measurement_end_date = measurement.measurement_end

                # Buscar facturas que coincidan con el período de medición
                invoices = Invoice.objects.filter(
                    billing_period_start__lte=measurement_end_date,
                    billing_period_end__gte=measurement_start_date
                )

                # Si no se encuentra ninguna factura que coincida con las fechas, retornar un error
                if not invoices.exists():
                    return JsonResponse({"error": "No matching invoices found."}, status=404)

                # Supongamos que hay solo una factura que coincide. Si hay más, debes decidir cómo manejarlas.
                invoice = invoices.first()

        # Una vez que tenemos tanto la factura como la medición, ahora realizamos las comparaciones de consumo

        # Obtener los detalles de consumo de la factura y medición
        invoice_consumption = invoice.data.get("detalles_consumo", None) if invoice else None
        measurement_consumption = measurement.data.get("consumo_por_franja_horaria", None) if measurement else None

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
            "consumo_total_kwh": {
                "factura": consumo_total_invoice,
                "medicion": consumo_total_measurement,
                "diferencia": round(consumo_total_invoice - consumo_total_measurement, 2),
                "coincide": consumo_total_invoice == consumo_total_measurement
            },
            "consumo_punta": {
                "factura": consumo_punta_invoice,
                "medicion": consumo_punta_measurement,
                "diferencia": round(consumo_punta_invoice - consumo_punta_measurement, 2),
                "coincide": consumo_punta_invoice == consumo_punta_measurement
            },
            "consumo_valle": {
                "factura": consumo_valle_invoice,
                "medicion": consumo_valle_measurement,
                "diferencia": round(consumo_valle_invoice - consumo_valle_measurement, 2),
                "coincide": consumo_valle_invoice == consumo_valle_measurement
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
        total_to_pay_matches = invoice_consumption.get("desglose_cargos", {}).get("total_a_pagar", 0) == round(total_to_pay, 2) if invoice else False

        # Comparar las fechas (para 'dates_match')
        dates_match = False
        if invoice and measurement:
            if invoice_start_date and invoice_end_date and measurement.measurement_start and measurement.measurement_end:
                # Comparar las fechas de inicio y fin
                dates_match = (invoice_start_date == measurement.measurement_start and invoice_end_date == measurement.measurement_end)

        # Crear el JSON de respuesta con los datos adicionales
        response_data = {
            "periodo_facturacion": {
                "fecha_inicio_factura": invoice.billing_period_start.strftime('%Y-%m-%d') if invoice else None,  # Convertir a string
                "fecha_fin_factura": invoice.billing_period_end.strftime('%Y-%m-%d') if invoice else None,  # Convertir a string
                "fecha_inicio_medicion": measurement.measurement_start.strftime('%Y-%m-%d'),  # Convertir a string
                "fecha_fin_medicion": measurement.measurement_end.strftime('%Y-%m-%d'),  # Convertir a string
                "dias_facturados": (invoice_end_date - invoice_start_date).days + 1 if invoice_start_date and invoice_end_date else None,
                "coincide": dates_match
            },
            "detalles_consumo": consumption_details,
            "total_a_pagar": {
                "factura": invoice_consumption.get("desglose_cargos", {}).get("total_a_pagar", 0) if invoice else None,
                "medicion": total_estimated_with_time_of_use
            }
        }

        return JsonResponse(response_data, safe=False)

    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)
