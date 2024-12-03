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
    Carga datos de mediciones desde un archivo JSON.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Buscar un usuario genérico
    default_user = User.objects.first()  # Usa el primer usuario disponible como predeterminado

    if not default_user:
        print("No se encontró ningún usuario en la base de datos. No se pueden cargar las mediciones.")
        return

    for item in data:
        try:
            # Asignar usuario predeterminado a todas las mediciones
            Measurement.objects.create(
                user=default_user,
                data=item  # Carga directamente todo el JSON en el campo `data`
            )
            print(f"Medición creada correctamente para el usuario {default_user.fullname}.")
        except Exception as e:
            print(f"Error al crear medición: {e}")

if __name__ == "__main__":
    # Ruta al archivo JSON
    load_measurements("site_app/measurements/scripts/data_measurements.json")
