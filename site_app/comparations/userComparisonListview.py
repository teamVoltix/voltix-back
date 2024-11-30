from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from voltix.models import InvoiceComparison
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserComparisonListView(APIView):
    """
    Retrieve the list of comparisons for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get User Comparisons",
        operation_description="Returns a list of invoice comparisons for the authenticated user.",
        responses={
            200: openapi.Response(
                description="Comparison list retrieved successfully.",
                examples={
                    "application/json": [
                        {
                            "invoice_id": 123,
                            "measurement_id": 456,
                            "comparison_status": "Valid",
                            "created_at": "2024-11-29T10:00:00",
                            "result": {"coincidencia_general": True}
                        }
                    ]
                }
            ),
            403: openapi.Response(description="Forbidden."),
            404: openapi.Response(description="No comparisons found.")
        }
    )
    def get(self, request):
        try:
            # Obtener todas las comparaciones del usuario autenticado
            comparisons = InvoiceComparison.objects.filter(user=request.user)

            if not comparisons.exists():
                return Response({"message": "No comparisons found."}, status=status.HTTP_404_NOT_FOUND)

            comparison_data = [
                {
                    "invoice_id": comparison.invoice.id,
                    "measurement_id": comparison.measurement.id,
                    "comparison_status": "Sin descrepancia" if comparison.is_comparison_valid else "Con descrepancia",
                    "created_at": comparison.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "result": comparison.comparison_results
                }
                for comparison in comparisons
            ]

            return Response(comparison_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserComparisonDetailView(APIView):
    """
    Retrieve the details of a specific comparison.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get Specific Comparison Details",
        operation_description="Returns the detailed results of a specific comparison.",
        responses={
            200: openapi.Response(
                description="Comparison details retrieved successfully.",
                examples={
                    "application/json": {
                        "invoice_id": 123,
                        "measurement_id": 456,
                        "comparison_status": "Valid",
                        "created_at": "2024-11-29T10:00:00",
                        "result": {
                            "periodo_facturacion": {
                                "fecha_inicio_factura": "2023-01-01",
                                "fecha_fin_factura": "2023-01-31"
                            },
                            "detalles_consumo": {
                                "total_consumption_kwh": {
                                    "invoice": 500,
                                    "measurement": 495,
                                    "difference": 5.0
                                }
                            },
                            "total_a_pagar": {
                                "factura": 100.0,
                                "calculo_medicion": 98.56
                            },
                            "coincidencia_general": True
                        }
                    }
                }
            ),
            403: openapi.Response(description="Forbidden."),
            404: openapi.Response(description="Comparison not found.")
        }
    )
    def get(self, request, comparison_id):
        try:
            # Obtener la comparación específica por ID
            comparison = InvoiceComparison.objects.get(id=comparison_id, user=request.user)

            comparison_data = {
                "invoice_id": comparison.invoice.id,
                "measurement_id": comparison.measurement.id,
                "comparison_status": "Sin descrepancia" if comparison.is_comparison_valid else "Con descrepancia",
                "created_at": comparison.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "result": comparison.comparison_results
            }

            return Response(comparison_data, status=status.HTTP_200_OK)

        except InvoiceComparison.DoesNotExist:
            return Response({"error": "Comparison not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)