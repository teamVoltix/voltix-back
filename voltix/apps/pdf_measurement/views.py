from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
from apps.general.models import InvoiceComparison

@api_view(['GET'])
# @permission_classes([IsAuthenticated])  # Quita esta línea
def download_report(request):
    try:
        # Obtener el ID de comparación
        comparison_id = request.query_params.get('id')
        if not comparison_id:
            return Response({"error": "Comparison ID is required."}, status=400)

        # Buscar el objeto de comparación
        comparison = InvoiceComparison.objects.filter(id=comparison_id, user=request.user).first()
        if not comparison:
            return Response({"error": "No comparison data found for the provided ID."}, status=404)

        # Preparar datos para el microservicio
        comparison_data = {
            "user": request.user.username,
            "billing_period_start": comparison.invoice.billing_period_start.isoformat(),
            "billing_period_end": comparison.invoice.billing_period_end.isoformat(),
            "measurement_start": comparison.measurement.measurement_start.isoformat(),
            "measurement_end": comparison.measurement.measurement_end.isoformat(),
            "comparison_results": comparison.comparison_results,
            "is_comparison_valid": comparison.is_comparison_valid,
        }

        # Hacer la solicitud al microservicio
        microservice_url = "http://127.0.0.1:8002/download_report"
        response = requests.post(microservice_url, json=comparison_data)

        # Devolver el PDF generado al cliente
        if response.status_code == 200:
            pdf = response.content
            http_response = HttpResponse(pdf, content_type="application/pdf")
            http_response['Content-Disposition'] = 'attachment; filename="comparison_report.pdf"'
            return http_response
        else:
            return Response({"error": "Failed to generate PDF."}, status=500)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
