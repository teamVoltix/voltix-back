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

    # Evaluar si la comparación es válida
    # Si alguna de las diferencias es diferente de 0, la comparación no es válida
    is_comparison_valid = all(
        detalle["diferencia"] == 0 for detalle in detalles_consumo.values()
    ) and periodo_facturacion == "Coincide"

    # Retornar los resultados como un JsonResponse con el campo is_comparison_valid
    return JsonResponse({
        "periodo_facturacion": periodo_facturacion,
        "detalles_consumo": detalles_consumo,
        "is_comparison_valid": is_comparison_valid,
    })
