from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from voltix.models import Measurement

# Esquema de respuesta para una medición
measurement_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de la medición'),
        'date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de la medición'),
        'value': openapi.Schema(type=openapi.TYPE_NUMBER, description='Valor de la medición'),
        'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='Datos adicionales en formato JSON'),
    }
)

def index(request):
    return HttpResponse("MEASUREMENTS YEY")

# 1. GET para obtener mediciones del usuario autenticado
@swagger_auto_schema(
    method="get",
    operation_description="Devuelve las mediciones asociadas al usuario autenticado",
    responses={
        200: openapi.Response(
            description="Mediciones del usuario autenticado",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del usuario'),
                    'measurements': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=measurement_schema,
                        description='Lista de mediciones del usuario'
                    ),
                }
            )
        ),
        401: openapi.Response(description="No autorizado. El token no es válido o ha expirado"),
        500: openapi.Response(description="Error interno del servidor"),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_measurements(request):
    """
    Retorna las mediciones asociadas al usuario autenticado.
    """
    try:
        user = request.user 
        measurements = Measurement.objects.filter(user=user).values('id', 'date', 'value', 'data')
        return Response({"user": user.fullname, "measurements": list(measurements)})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# 2. GET para obtener todas las mediciones
@swagger_auto_schema(
    method="get",
    operation_description="Devuelve todas las mediciones existentes en la base de datos",
    responses={
        200: openapi.Response(
            description="Todas las mediciones en el sistema",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'measurements': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=measurement_schema,
                        description='Lista de todas las mediciones'
                    ),
                }
            )
        ),
        500: openapi.Response(description="Error interno del servidor"),
    },
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_measurements(request):
    """
    Retorna todas las mediciones existentes en la base de datos.
    """
    try:
        measurements = Measurement.objects.all().values('id', 'user__fullname', 'date', 'value', 'data')
        return Response({"measurements": list(measurements)})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
