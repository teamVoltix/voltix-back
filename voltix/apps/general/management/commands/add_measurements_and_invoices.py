from django.core.management.base import BaseCommand
from apps.general.models import User, Measurement, Invoice  # Replace with your actual app and models
from datetime import datetime, timedelta
import json
import random

class Command(BaseCommand):
    help = 'Add measurements and invoices for users for the last 6 months'

    def handle(self, *args, **kwargs):
        # Fetch all users starting from user_id = 2
        users = User.objects.filter(user_id__gte=2)

        start_month = 6  # June
        end_month = 11  # November
        year = 2023

        for user in users:
            for month in range(start_month, end_month + 1):
                # Generate start and end dates
                month_start = datetime(year, month, 1)
                last_day = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                month_end = last_day

                # Generate dynamic consumption data for measurement
                consumo_total_measurement = 300 + user.user_id * 10 + month * 5
                punta_measurement = round(consumo_total_measurement * 0.7, 2)
                valle_measurement = round(consumo_total_measurement * 0.3, 2)

                # Measurement data
                measurement_data = {
                    "periodo_medicion": {
                        "inicio": month_start.strftime('%Y-%m-%d'),
                        "fin": month_end.strftime('%Y-%m-%d')
                    },
                    "consumo_total": consumo_total_measurement,
                    "consumo_por_franja_horaria": {
                        "punta": punta_measurement,
                        "valle": valle_measurement
                    },
                    "potencia_maxima_demandada": {
                        "punta": round(punta_measurement * 0.045, 2),
                        "valle": round(valle_measurement * 0.06, 2)
                    },
                    "tension_promedio": 230,
                    "corriente_promedio": {
                        "punta": round(punta_measurement / 6.7, 2),
                        "valle": round(valle_measurement / 12.4, 2)
                    },
                    "factor_de_potencia_promedio": 0.91,
                    "eventos_registrados": {
                        "interrupciones": 1,
                        "caidas_de_tension": 3
                    }
                }

                # Add measurement
                measurement = Measurement(
                    user=user,
                    measurement_start=month_start,
                    measurement_end=month_end,
                    data=measurement_data,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                measurement.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Measurement added for user {user.fullname} ({user.user_id}) for {month_start.strftime('%B %Y')}."
                ))

                # Generate dynamic consumption data for invoice
                consumo_total_invoice = consumo_total_measurement + random.randint(-10, 10)  # Small difference
                punta_invoice = round(consumo_total_invoice * 0.7, 2)
                valle_invoice = round(consumo_total_invoice * 0.3, 2)

                # Invoice data
                invoice_data = {
                    "nombre_cliente": user.fullname,
                    "numero_referencia": f"{123456789 + user.user_id}/00{month}",
                    "fecha_emision": (month_end + timedelta(days=1)).strftime('%Y-%m-%d'),
                    "periodo_facturacion": {
                        "inicio": month_start.strftime('%Y-%m-%d'),
                        "fin": month_end.strftime('%Y-%m-%d'),
                        "dias": (month_end - month_start).days + 1
                    },
                    "forma_pago": "Domiciliación bancaria",
                    "fecha_cargo": (month_end + timedelta(days=10)).strftime('%Y-%m-%d'),
                    "desglose_cargos": {
                        "costo_potencia": round(consumo_total_invoice * 0.1, 2),
                        "costo_energia": round(consumo_total_invoice * 0.12, 2),
                        "descuentos": round(consumo_total_invoice * 0.015, 2),
                        "impuestos": round(consumo_total_invoice * 0.18, 2),
                        "total_a_pagar": round(
                            consumo_total_invoice * 0.1 +
                            consumo_total_invoice * 0.12 +
                            consumo_total_invoice * 0.18 -
                            consumo_total_invoice * 0.015, 2
                        )
                    },
                    "detalles_consumo": {
                        "consumo_punta": punta_invoice,
                        "consumo_valle": valle_invoice,
                        "consumo_total": consumo_total_invoice,
                        "precio_efectivo_energia": 0.1121
                    }
                }

                # Add invoice
                invoice = Invoice(
                    user=user,
                    billing_period_start=month_start,
                    billing_period_end=month_end,
                    data=invoice_data,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                invoice.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Invoice added for user {user.fullname} ({user.user_id}) for {month_start.strftime('%B %Y')}."
                ))
