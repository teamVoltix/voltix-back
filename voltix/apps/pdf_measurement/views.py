import os
import tempfile
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
import requests
from apps.general.models import InvoiceComparison

@api_view(['GET'])
def download_report(request):
    try:
        # Obtener el ID de comparación
        comparison_id = request.query_params.get('id')
        if not comparison_id:
            return JsonResponse({"error": "Comparison ID is required."}, status=400)

        # Buscar el objeto de comparación
        comparison = InvoiceComparison.objects.filter(id=comparison_id, user=request.user).first()
        if not comparison:
            return JsonResponse({"error": "No comparison data found for the provided ID."}, status=404)

        # Preparar datos para el microservicio
        comparison_data = {
            "user": request.user.fullname,
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

        if response.status_code == 200:
            pdf = response.content

            # Guardar el PDF temporalmente en la carpeta "reports" de MEDIA_ROOT
            reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)  # Crear la carpeta si no existe

            # Crear un archivo temporal en la carpeta reports
            file_path = os.path.join(reports_dir, f"comparison_report_{comparison_id}.pdf")

            # Escribir el contenido del PDF en el archivo
            with open(file_path, 'wb') as f:
                f.write(pdf)

            # Devolver el PDF generado al cliente como archivo descargable
            http_response = HttpResponse(pdf, content_type="application/pdf")
            http_response['Content-Disposition'] = f'attachment; filename="comparison_report_{comparison_id}.pdf"'
            return http_response

        else:
            return JsonResponse({"error": "Failed to generate PDF."}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
