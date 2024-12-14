from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.voltix.models import Invoice
from .serializers import InvoiceSerializer
from apps.voltix.utils.comparison_status import annotate_comparison_status  #utility function
# Swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

invoice_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the invoice"),
        "user_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="User ID associated with the invoice"),
        "billing_period_start": openapi.Schema(type=openapi.FORMAT_DATE, description="Billing period start date"),
        "billing_period_end": openapi.Schema(type=openapi.FORMAT_DATE, description="Billing period end date"),
        "data": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="Detailed invoice data",
            properties={
                "mandato": openapi.Schema(type=openapi.TYPE_STRING, description="Mandate ID"),
                "forma_pago": openapi.Schema(type=openapi.TYPE_STRING, description="Payment method"),
                "fecha_cargo": openapi.Schema(type=openapi.FORMAT_DATE, description="Charge date"),
                "fecha_emision": openapi.Schema(type=openapi.FORMAT_DATE, description="Issue date"),
                "nombre_cliente": openapi.Schema(type=openapi.TYPE_STRING, description="Customer name"),
                "desglose_cargos": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Cost breakdown",
                    properties={
                        "impuestos": openapi.Schema(type=openapi.TYPE_NUMBER, description="Taxes"),
                        "descuentos": openapi.Schema(type=openapi.TYPE_NUMBER, description="Discounts"),
                        "costo_energia": openapi.Schema(type=openapi.TYPE_NUMBER, description="Energy cost"),
                        "total_a_pagar": openapi.Schema(type=openapi.TYPE_NUMBER, description="Total amount due"),
                        "costo_potencia": openapi.Schema(type=openapi.TYPE_NUMBER, description="Power cost"),
                    },
                ),
                "detalles_consumo": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Consumption details",
                    properties={
                        "consumo_punta": openapi.Schema(type=openapi.TYPE_NUMBER, description="Peak consumption"),
                        "consumo_total": openapi.Schema(type=openapi.TYPE_NUMBER, description="Total consumption"),
                        "consumo_valle": openapi.Schema(type=openapi.TYPE_NUMBER, description="Valley consumption"),
                        "precio_efectivo_energia": openapi.Schema(type=openapi.TYPE_NUMBER, description="Effective energy price"),
                    },
                ),
                "numero_referencia": openapi.Schema(type=openapi.TYPE_STRING, description="Reference number"),
                "periodo_facturacion": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Billing period details",
                    properties={
                        "inicio": openapi.Schema(type=openapi.FORMAT_DATE, description="Start date"),
                        "fin": openapi.Schema(type=openapi.FORMAT_DATE, description="End date"),
                        "dias": openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of days"),
                    },
                ),
            },
        ),
        "comparison_status": openapi.Schema(type=openapi.TYPE_STRING, description="Comparison status of the invoice"),
        "created_at": openapi.Schema(type=openapi.FORMAT_DATETIME, description="Creation timestamp"),
        "updated_at": openapi.Schema(type=openapi.FORMAT_DATETIME, description="Last update timestamp"),
    },
)

# Example response for Swagger
example_response = {
    "status": "success",
    "message": "Data retrieved successfully!",
    "user": {
        "id": 4,
        "name": "John Smith",
        "email": "john.smith@outlook.com"
    },
    "invoices": [
        {
            "id": 1,
            "comparison_status": "Con discrepancia",
            "billing_period_start": "2020-12-01",
            "billing_period_end": "2020-12-22",
            "data": {
                "mandato": "E00020920449122600010001",
                "forma_pago": "Domiciliación bancaria",
                "fecha_cargo": "2021-01-04",
                "fecha_emision": "2020-12-28",
                "nombre_cliente": "ALBERTO CAIMI",
                "desglose_cargos": {
                    "impuestos": 77.94,
                    "descuentos": 281.0,
                    "costo_energia": 25.68,
                    "total_a_pagar": 436.36,
                    "costo_potencia": 20.3
                },
                "detalles_consumo": {
                    "consumo_punta": 67.0,
                    "consumo_total": 213.0,
                    "consumo_valle": 146.0,
                    "precio_efectivo_energia": 0.1121
                },
                "numero_referencia": "012300620608/0015",
                "periodo_facturacion": {
                    "inicio": "2020-12-01",
                    "fin": "2020-12-22",
                    "dias": 21
                }
            },
            "created_at": "2024-11-28T11:15:42.410179Z",
            "updated_at": "2024-11-28T11:15:42.410186Z",
            "user": 4
        }
    ]
}

class UserInvoiceListView(APIView):
    """
    API view to retrieve a list of invoices with their comparison status for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve invoices with their comparison status for the authenticated user.",
        responses={
            200: openapi.Response(
                description="List of invoices with comparison status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "status": openapi.Schema(type=openapi.TYPE_STRING, description="Status of the response"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="Response message"),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="User ID"),
                                "name": openapi.Schema(type=openapi.TYPE_STRING, description="Full name of the user"),
                                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email of the user"),
                            },
                        ),
                        "invoices": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=invoice_schema,
                            description="List of invoices with their comparison status",
                        ),
                    },
                ),
                examples={
                    "application/json": example_response  # Add example response here
                },
            ),
            401: openapi.Response(description="Unauthorized. User is not authenticated."),
            500: openapi.Response(description="Internal server error."),
        },
    )
    def get(self, request):
        try:
            user = request.user

            # Retrieve invoices for the authenticated user
            invoices = Invoice.objects.filter(user=user)

            # Annotate invoices with their comparison status
            annotated_invoices = annotate_comparison_status(invoices, "invoice")

            # Serialize the annotated invoices
            serializer = InvoiceSerializer(annotated_invoices, many=True)

            response_data = {
                "status": "success",
                "message": "Data retrieved successfully!",
                "user": {
                    "id": user.id,
                    "name": user.fullname,
                    "email": user.email,
                },
                "invoices": serializer.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "An error occurred while retrieving invoices.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
