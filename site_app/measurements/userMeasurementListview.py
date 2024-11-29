from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from voltix.models import Measurement
from .serializers import MeasurementSerializer
from voltix.utils.comparison_status import annotate_comparison_status
#swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
            ),
            401: openapi.Response(description="Unauthorized. The token is invalid or has expired."),
            500: openapi.Response(description="Internal server error."),
        },
    )


    def get(self, request):
        try:
            user = request.user

            measurements = Measurement.objects.filter(user=user)

            annotated_measurements = annotate_comparison_status(measurements, "measurement")

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

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "An error occurred while retrieving measurements.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
