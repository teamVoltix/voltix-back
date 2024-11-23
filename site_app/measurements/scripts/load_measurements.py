import os
import sys
import django
import json

# Añade el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "site_app.settings")  
django.setup()

from voltix.models import Measurement, User  

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

            # Crea la medición
            Measurement.objects.create(
                user=user,
                date=item["date"],
                value=item["value"],
                data=item["data"]  # Campo JSON
            )
            print(f"Medición creada para el usuario {user.fullname}")
        except User.DoesNotExist:
            print(f"Usuario con DNI {item['user_dni']} no encontrado. Saltando...")
        except Exception as e:
            print(f"Error al crear medición: {e}")

if __name__ == "__main__":
    # Ruta al archivo JSON
    load_measurements("site_app/measurements/scripts/data_measurements.json")
