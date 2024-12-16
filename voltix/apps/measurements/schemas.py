from drf_yasg import openapi

# Esquema para una medición individual
measurement_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de la medición'),
        'measurement_start': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Inicio de la medición'),
        'measurement_end': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Fin de la medición'),
        'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='Datos adicionales en formato JSON'),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Fecha de creación'),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Última actualización'),
    },
)