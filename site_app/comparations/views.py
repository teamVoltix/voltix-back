from django.http import JsonResponse
from datetime import datetime

def compare_invoice_and_measurement(invoice, measurement):
    # Comparar el período de facturación
    billing_period_matches = (
        "Matches" if invoice.billing_period_start == measurement.data["billing_period"]["start"]
        and invoice.billing_period_end == measurement.data["billing_period"]["end"]
        else "Does not match"
    )

    # Calcular los días facturados
    invoice_start_date = datetime.strptime(invoice.billing_period_start, "%Y-%m-%d")
    invoice_end_date = datetime.strptime(invoice.billing_period_end, "%Y-%m-%d")
    days_billed = (invoice_end_date - invoice_start_date).days + 1  # Incluye el día final

    # Detalles del consumo
    invoice_consumption = invoice.data["consumption_details"]
    measurement_consumption = measurement.data["consumption_details"]

    consumption_details = {
        "total_consumption": {
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

    # Calcular el importe estimado para el consumo total
    total_consumption_kWh = measurement_consumption["total_consumption"]  # Medición del consumo total
    price_per_kWh = 0.1121  # Precio por kWh (ejemplo de tarifa)
    electricity_tax_rate = 0.051127  # Tasa del impuesto sobre la electricidad
    vat_rate = 0.21  # IVA al 21%

    # Calcular el término de energía
    energy_term = total_consumption_kWh * price_per_kWh
    # Calcular el impuesto sobre la electricidad
    electricity_tax = energy_term * electricity_tax_rate
    # Calcular el subtotal antes de IVA
    subtotal = energy_term + electricity_tax
    # Calcular el IVA
    vat = subtotal * vat_rate
    # Calcular el total estimado
    total_estimated = subtotal + vat

    # Si hay discriminación horaria, calcular el total estimado para cada franja horaria
    if "peak_consumption" in measurement_consumption and "off_peak_consumption" in measurement_consumption:
        # Precio del kWh en punta y valle (ejemplo)
        peak_price = 0.15
        off_peak_price = 0.10
        peak_consumption_kWh = measurement_consumption["peak_consumption"]
        off_peak_consumption_kWh = measurement_consumption["off_peak_consumption"]

        # Calcular el consumo en punta
        peak_energy_term = peak_consumption_kWh * peak_price
        # Calcular el consumo en valle
        off_peak_energy_term = off_peak_consumption_kWh * off_peak_price
        # Calcular el término total de energía
        total_energy_term = peak_energy_term + off_peak_energy_term

        # Calcular el impuesto sobre la electricidad para el consumo total
        total_electricity_tax = total_energy_term * electricity_tax_rate
        total_subtotal = total_energy_term + total_electricity_tax
        total_vat = total_subtotal * vat_rate
        total_estimated_with_time_of_use = total_subtotal + total_vat
    else:
        total_estimated_with_time_of_use = total_estimated

    # Evaluar si la comparación es válida
    is_comparison_valid = all(
        detail["matches"] for detail in consumption_details.values()
    ) and billing_period_matches == "Matches"

    # Crear el JSON de respuesta con los datos adicionales
    response_data = {
        "billing_period": {
            "status": billing_period_matches,
            "invoice_start_date": invoice.billing_period_start,
            "invoice_end_date": invoice.billing_period_end,
            "measurement_start_date": measurement.data["billing_period"]["start"],
            "measurement_end_date": measurement.data["billing_period"]["end"],
            "days_billed": days_billed
        },
        "consumption_details": consumption_details,
        "total_estimated": round(total_estimated, 2),
        "total_estimated_with_time_of_use": round(total_estimated_with_time_of_use, 2),
        "total_consumption_kwh": {
            "invoice": invoice_consumption["total_consumption"],
            "measurement": measurement_consumption["total_consumption"]
        }
    }

    return JsonResponse(response_data), is_comparison_valid
