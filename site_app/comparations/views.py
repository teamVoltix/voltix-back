from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from datetime import datetime
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
            invoice = Invoice.objects.get(id=invoice_id, user=request.user)  # Buscar la factura solo del usuario autenticado
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Invoice not found."}, status=404)

        # Buscar la medición que coincida con el período de facturación de la factura
        invoice_start_date = invoice.billing_period_start  # Es de tipo datetime.date
        invoice_end_date = invoice.billing_period_end  # Es de tipo datetime.date

        # Buscar mediciones que coincidan con el período de facturación
        measurements = Measurement.objects.filter(
            user=request.user,  # Solo mediciones del usuario logueado
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
        measurement_consumption = measurement.data.get("consumo_total", None)

        # Si no se encuentran los detalles de consumo en la factura o medición, retornar un error
        if not invoice_consumption or not measurement_consumption:
            return JsonResponse({"error": "'detalles_consumo' or 'consumo_total' not found in invoice or measurement."}, status=404)

        # Asegurarse de que no haya valores None, reemplazarlos con 0
        consumo_total_invoice = invoice_consumption.get("consumo_total", 0) or 0
        consumo_total_measurement = measurement_consumption or 0

        # Detalles del consumo
        consumption_details = {
            "total_consumption_kwh": {
                "invoice": consumo_total_invoice,
                "measurement": consumo_total_measurement,
                "difference": round(consumo_total_invoice - consumo_total_measurement, 2),
                "matches": consumo_total_invoice == consumo_total_measurement
            }
        }

        # Calcular el importe total estimado para el consumo total (basado en medición)
        total_consumption_kWh = consumo_total_measurement
        price_per_kWh = 0.1121  # Precio por kWh (puedes cambiar esto según tus necesidades)
        electricity_tax_rate = 0.051127  # Tasa del impuesto sobre la electricidad
        vat_rate = 0.21  # IVA al 21%

        energy_term = total_consumption_kWh * price_per_kWh
        electricity_tax = energy_term * electricity_tax_rate
        subtotal = energy_term + electricity_tax
        vat = subtotal * vat_rate
        total_to_pay = subtotal + vat

        # Ahora accedemos correctamente al total_a_pagar desde el desglose_cargos de la factura
        total_a_pagar = invoice.data.get("desglose_cargos", {}).get("total_a_pagar", 0)

        # Comparar el total a pagar entre la factura y la medición
        total_to_pay_matches = total_a_pagar == round(total_to_pay, 2)

        # Comparar las fechas (para 'dates_match')
        dates_match = invoice_start_date == measurement.measurement_start.date() and invoice_end_date == measurement.measurement_end.date()

        # Crear el JSON de respuesta con los datos en español
        response_data = {
            "periodo_facturacion": {
                "fecha_inicio_factura": invoice.billing_period_start.strftime('%Y-%m-%d'),  # Convertir a string
                "fecha_fin_factura": invoice.billing_period_end.strftime('%Y-%m-%d'),  # Convertir a string
                "fecha_inicio_medicion": measurement.measurement_start.strftime('%Y-%m-%d'),  # Convertir a string
                "fecha_fin_medicion": measurement.measurement_end.strftime('%Y-%m-%d'),  # Convertir a string
                "dias_facturados": invoice.data.get("periodo_facturacion", {}).get("dias", 0),
                "coincide_fechas": dates_match
            },
            "detalles_consumo": consumption_details,
            "total_a_pagar": {
                "factura": total_a_pagar,  # Ahora correctamente toma el total a pagar de la factura
                "calculo_medicion": round(total_to_pay, 2),  # Valor calculado a partir de mediciones
                "coincide_total": total_to_pay_matches
            },
            "coincidencia_general": all(value["matches"] for value in consumption_details.values()) and total_to_pay_matches and dates_match
        }

        # Crear la instancia en InvoiceComparison
        InvoiceComparison.objects.create(
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
            "result": response_data
        }


        return Response(response, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
