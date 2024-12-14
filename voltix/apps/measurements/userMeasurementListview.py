from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.general.models import Measurement
from .serializers import MeasurementSerializer
from apps.general.utils.comparison_status import annotate_comparison_status
# swagger imports
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse

measurement_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the measurement"),
        "measurement_start": openapi.Schema(type=openapi.FORMAT_DATETIME, description="Start of measurement period"),
        "measurement_end": openapi.Schema(type=openapi.FORMAT_DATETIME, description="End of measurement period"),
        "data": openapi.Schema(type=openapi.TYPE_OBJECT, description="JSON data related to the measurement"),
        "created_at": openapi.Schema(type=openapi.FORMAT_DATETIME, description="Creation timestamp"),
        "updated_at": openapi.Schema(type=openapi.FORMAT_DATETIME, description="Last update timestamp"),
        "comparison_status": openapi.Schema(type=openapi.TYPE_STRING, description="Comparison status of the measurement"),
    },
)

# Example response
example_response = {
    "status": "success",
    "message": "Data retrieved successfully!",
    "user": {
        "id": 4,
        "name": "John Smith",
        "email": "john.smith@outlook.com"
    },
    "measurements": [
        {
            "id": 2,
            "comparison_status": "Con discrepancia",
            "measurement_start": "2023-10-01T00:00:00Z",
            "measurement_end": "2023-10-31T23:59:59Z",
            "data": {
                "consumo_total": 213,
                "periodo_medicion": {
                    "inicio": "2023-10-01",
                    "fin": "2023-10-31"
                },
                "tension_promedio": 230,
                "corriente_promedio": {
                    "punta": 23.9,
                    "valle": 13.0
                },
                "eventos_registrados": {
                    "interrupciones": 0,
                    "caidas_de_tension": 2
                },
                "potencia_maxima_demandada": {
                    "punta": 5.5,
                    "valle": 3.0
                },
                "consumo_por_franja_horaria": {
                    "punta": 146.0,
                    "valle": 67.0
                },
                "factor_de_potencia_promedio": 0.95
            },
            "created_at": "2024-11-28T11:14:03.317972Z",
            "updated_at": "2024-11-28T11:14:03.317972Z",
            "user": 4
        },
        # Add additional measurements here for brevity
    ]
}

class UserMeasurementListView(APIView):
    """
    API view to retrieve a list of measurements with their comparison status for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve the measurements associated with the authenticated user.",
        responses={
            200: openapi.Response(
                description="Authenticated user's measurements",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, description="Status of the response"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="Message regarding the request"),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="User ID"),
                                "name": openapi.Schema(type=openapi.TYPE_STRING, description="Full name of the user"),
                                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email of the user"),
                            },
                        ),
                        "measurements": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=measurement_schema,
                            description="List of measurements associated with the user",
                        ),
                    },
                ),
                examples={
                    "application/json": example_response  # Example response
                },
            ),
            401: openapi.Response(description="Unauthorized. The token is invalid or has expired."),
            500: openapi.Response(description="Internal server error."),
        },
    )
    def get(self, request):
        try:
            user = request.user

            # Retrieve measurements for the authenticated user
            measurements = Measurement.objects.filter(user=user)

            # Annotate measurements with comparison status
            annotated_measurements = annotate_comparison_status(measurements, "measurement")

            # Serialize the annotated measurements
            serializer = MeasurementSerializer(annotated_measurements, many=True)

            response_data = {
                "status": "success",
                "message": "Data retrieved successfully!",
                "user": {
                    "id": user.id,
                    "name": user.fullname,
                    "email": user.email,
                },
                "measurements": serializer.data,
            }

            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "An error occurred while retrieving measurements.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
