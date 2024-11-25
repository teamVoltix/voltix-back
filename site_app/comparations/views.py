from django.http import JsonResponse

def comparar_factura_y_medicion(invoice, measurement):
    # Comparar período de facturación
    periodo_facturacion = (
        "Coincide" if invoice.billing_period_start == measurement.data["periodo_facturacion"]["inicio"]
        and invoice.billing_period_end == measurement.data["periodo_facturacion"]["fin"]
        else "No coincide"
    )

    # Comparar detalles de consumo
    consumo_factura = invoice.data["detalles_consumo"]
    consumo_medicion = measurement.data["detalles_consumo"]

    detalles_consumo = {
        "consumo_total": {
            "factura": consumo_factura["consumo_total"],
            "medicion": consumo_medicion["consumo_total"],
            "diferencia": round(consumo_factura["consumo_total"] - consumo_medicion["consumo_total"], 2),
        },
        "consumo_punta": {
            "factura": consumo_factura["consumo_punta"],
            "medicion": consumo_medicion["consumo_punta"],
            "diferencia": round(consumo_factura["consumo_punta"] - consumo_medicion["consumo_punta"], 2),
        },
    }

    # Retornar los resultados como un JsonResponse
    return JsonResponse({
        "periodo_facturacion": periodo_facturacion,
        "detalles_consumo": detalles_consumo,
    })
