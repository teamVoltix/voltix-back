from django.db.models import OuterRef, Subquery, Case, When, Value, CharField, Exists
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from voltix.models import Invoice, InvoiceComparison
from .serializers import InvoiceSerializer

class UserInvoiceListView(APIView):
    """
    API view to retrieve a list of invoices with their comparison status.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Subquery to check if a comparison exists for each invoice
            comparison_subquery = InvoiceComparison.objects.filter(invoice=OuterRef('pk'))

            # Annotate the invoices with their comparison status
            invoices = Invoice.objects.annotate(
                comparison_status=Case(
                    # No comparison exists
                    When(~Exists(comparison_subquery), then=Value("Sin comparasion")),
                    # A valid comparison exists
                    When(Exists(comparison_subquery.filter(is_comparison_valid=True)), then=Value("Sin discrepancia")),
                    # An invalid comparison exists
                    When(Exists(comparison_subquery.filter(is_comparison_valid=False)), then=Value("Con discrepancia")),
                    # Default case
                    default=Value("unknown"),
                    output_field=CharField(),
                )
            )

            # Serialize the data
            serializer = InvoiceSerializer(invoices, many=True)

            # Enhanced response structure
            response_data = {
                "status": "success",
                "message": "Data retrieved successfully!",
                "user": {
                    "id": request.user.id,
                    "name": request.user.fullname,
                    "email": request.user.email,
                },
                "invoices": serializer.data,  # Send invoices as a structured list
            }

            # Return a formatted response
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected errors gracefully
            return Response(
                {
                    "status": "error",
                    "message": "An error occurred while retrieving invoices.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
