from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from voltix.models import Invoice
from .serializers import InvoiceSerializer
from voltix.utils.comparison_status import annotate_comparison_status  # Import the utility function


class UserInvoiceListView(APIView):
    """
    API view to retrieve a list of invoices with their comparison status for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user

            invoices = Invoice.objects.filter(user=user)
            annotated_invoices = annotate_comparison_status(invoices, "invoice")

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
