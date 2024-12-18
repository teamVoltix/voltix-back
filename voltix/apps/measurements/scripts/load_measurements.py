import os
import sys
import django
import json
from datetime import datetime
from django.utils.timezone import make_aware

# Añade el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "site_app.settings.base")  
django.setup()

from general.models import Measurement, User  

def load_measurements(file_path):
    """
    Carga datos de mediciones desde un archivo JSON
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    for item in data:
        try:
            # Busca el usuario por DNI
            user = User.objects.get(dni=item["user_dni"])

            # Convertir las fechas a objetos conscientes de la zona horaria
            measurement_start = make_aware(datetime.strptime(item["measurement_start"], "%Y-%m-%d"))
            measurement_end = make_aware(datetime.strptime(item["measurement_end"], "%Y-%m-%d"))

            # Extraer y transformar los datos según el nuevo formato
            measurement_data = {
                "consumo_total": item["data"]["consumo_total"],
                "periodo_medicion": {
                    "inicio": item["data"]["periodo_medicion"]["inicio"],
                    "fin": item["data"]["periodo_medicion"]["fin"],
                },
                "tension_promedio": item["data"]["tension_promedio"],
                "corriente_promedio": {
                    "punta": item["data"]["corriente_promedio"]["punta"],
                    "valle": item["data"]["corriente_promedio"]["valle"],
                },
                "eventos_registrados": {
                    "interrupciones": item["data"]["eventos_registrados"]["interrupciones"],
                    "caidas_de_tension": item["data"]["eventos_registrados"]["caidas_de_tension"],
                },
                "potencia_maxima_demandada": {
                    "punta": item["data"]["potencia_maxima_demandada"]["punta"],
                    "valle": item["data"]["potencia_maxima_demandada"]["valle"],
                },
                "consumo_por_franja_horaria": {
                    "punta": item["data"]["consumo_por_franja_horaria"]["punta"],
                    "valle": item["data"]["consumo_por_franja_horaria"]["valle"],
                },
                "factor_de_potencia_promedio": item["data"]["factor_de_potencia_promedio"],
            }

            # Crea la medición con measurement_start y measurement_end
            Measurement.objects.create(
                user=user,
                data=measurement_data,
                measurement_start=measurement_start,
                measurement_end=measurement_end
            )
            print(f"Medición creada para el usuario {user.fullname}")
        except User.DoesNotExist:
            print(f"Usuario con DNI {item['user_dni']} no encontrado. Saltando...")
        except Exception as e:
            print(f"Error al crear medición: {e}")

if __name__ == "__main__":
    # Ruta al archivo JSON
    load_measurements("site_app/measurements/scripts/data_measurements.json")
