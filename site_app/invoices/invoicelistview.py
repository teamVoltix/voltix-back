from django.db.models import OuterRef, Subquery, Case, When, Value, CharField
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from voltix.models import Invoice, InvoiceComparison
from .serializers import InvoiceSerializer
from django.db.models import Case, Value, CharField, When, Exists, OuterRef

class InvoiceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        comparison_subquery = InvoiceComparison.objects.filter(
            invoice=OuterRef('pk')
        )

        invoices = Invoice.objects.annotate(
            estado=Case(
                When(~Exists(comparison_subquery), then=Value("Sin comparasion")),
                When(Exists(comparison_subquery.filter(is_comparison_valid=True)), then=Value("Sin discrepancia")),
                When(Exists(comparison_subquery.filter(is_comparison_valid=False)), then=Value("Con discrepancia")),
                default=Value("unknown"),
                output_field=CharField(),
            )
        )

        serializer = InvoiceSerializer(invoices, many=True)
        return Response(
            {
                "status": "success",
                "message": "Data retrieved successfully!",
                "data": serializer.data
            }, 
            status=status.HTTP_200_OK
)