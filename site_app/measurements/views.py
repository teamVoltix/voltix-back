from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi # cambios
from voltix.models import Measurement
from .schemas import measurement_schema
from rest_framework.views import APIView
from voltix.utils.comparison_status import annotate_comparison_status
from rest_framework import status

# Esquema de respuesta para una medición
# measurement_schema = openapi.Schema(
#     type=openapi.TYPE_OBJECT,
#     properties={
#         'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de la medición'),
#         'date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Fecha de la medición'),
#         'value': openapi.Schema(type=openapi.TYPE_NUMBER, description='Valor de la medición'),
#         'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='Datos adicionales en formato JSON'),
#     }
# )

def index(request):
    return HttpResponse("MEASUREMENTS YEY")


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
        measurements = Measurement.objects.all().values('id', 'user__fullname', 'measurement_start', 'measurement_end', 'data', 'created_at', 'updated_at'
)
        return Response({"measurements": list(measurements)})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


class MeasurementDetailView(APIView):
    """
    API view to retrieve a single measurement by its ID, annotated with its comparison status.
    """
    permission_classes = [IsAuthenticated]


    @swagger_auto_schema(
    operation_description="Retrieve a specific measurement by its ID, annotated with its comparison status.",
    responses={
        200: openapi.Response(
            description="Successfully retrieved the measurement details",
            schema=measurement_schema,  # Use the imported schema here
            examples={
                "application/json": {
                    "id": 1,
                    "measurement_start": "2023-02-01T00:00:00Z",
                    "measurement_end": "2023-02-28T00:00:00Z",
                    "data": {
                        "consumo_total": 220,
                        "periodo_medicion": {
                            "fin": "2023-02-28",
                            "inicio": "2023-02-01"
                        },
                        "tension_promedio": 230,
                        "corriente_promedio": {
                            "punta": 24.0,
                            "valle": 13.5
                        },
                        "eventos_registrados": {
                            "interrupciones": 1,
                            "caidas_de_tension": 1
                        },
                        "potencia_maxima_demandada": {
                            "punta": 6.0,
                            "valle": 3.5
                        },
                        "consumo_por_franja_horaria": {
                            "punta": 150.0,
                            "valle": 70.0
                        },
                        "factor_de_potencia_promedio": 0.94
                    },
                    "created_at": "2024-12-01T09:44:15.658163Z",
                    "updated_at": "2024-12-01T09:44:15.658163Z",
                    "comparison_status": "Con discrepancia"
                }
            }
        ),
        404: openapi.Response(description="Measurement not found"),
        500: openapi.Response(description="Internal server error"),
    },
    manual_parameters=[
        openapi.Parameter(
            'measurement_id',
            openapi.IN_PATH,
            description="ID of the measurement to retrieve",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
    ],
)



    def get(self, request, measurement_id):
        try:
            measurement = Measurement.objects.filter(pk=measurement_id,user=request.user)

            if not measurement.exists():
                return Response(
                    {"error": f"Measurement with ID {measurement_id} not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            annotated_measurement = annotate_comparison_status(measurement, "measurement").first()

            if not annotated_measurement:
                return Response(
                    {"error": f"Measurement with ID {measurement_id} not found after annotation."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            response_data = {
                "id": annotated_measurement.id,
                "measurement_start": annotated_measurement.measurement_start,
                "measurement_end": annotated_measurement.measurement_end,
                "data": annotated_measurement.data,
                "created_at": annotated_measurement.created_at,
                "updated_at": annotated_measurement.updated_at,
                "comparison_status": annotated_measurement.comparison_status,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "error": "An error occurred while retrieving the measurement.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
