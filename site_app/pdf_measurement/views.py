from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from weasyprint import HTML
from voltix.models import InvoiceComparison

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_report(request):
    try:
        print("Received request to download report.")
        
        # Obtener el ID de comparación
        comparison_id = request.query_params.get('id')
        print(f"Comparison ID received: {comparison_id}")
        
        if not comparison_id:
            print("Comparison ID is required.")
            return Response({"error": "Comparison ID is required."}, status=400)

        # Buscar el objeto de comparación
        comparison = InvoiceComparison.objects.filter(id=comparison_id, user=request.user).first()
        print(f"Fetched comparison: {comparison}")

        if not comparison:
            print("No comparison data found for the provided ID.")
            return Response({"error": "No comparison data found for the provided ID."}, status=404)

        # Preparar datos para el reporte
        billing_period = {
            "status": "Valid" if comparison.is_comparison_valid else "Invalid",
            "invoice_start_date": comparison.invoice.billing_period_start,
            "invoice_end_date": comparison.invoice.billing_period_end,
            "measurement_start_date": comparison.measurement.measurement_start,
            "measurement_end_date": comparison.measurement.measurement_end,
            "days_billed": (comparison.invoice.billing_period_end - comparison.invoice.billing_period_start).days
        }
        print(f"Billing period data prepared: {billing_period}")

        # Datos del resultado de la comparación
        comparison_results = comparison.comparison_results
        print(f"Comparison results: {comparison_results}")

        consumption_details = {
            "Invoice": {
                "invoice": comparison_results['consumption_details']['total_consumption_kwh']['invoice'],
                "measurement": comparison_results['consumption_details']['total_consumption_kwh']['measurement'],
                "difference": comparison_results['consumption_details']['total_consumption_kwh']['difference'],
            }
        }
        print(f"Consumption details extracted: {consumption_details}")

        total_estimated = comparison_results.get("total_estimated_with_time_of_use")

        # Renderizado manual del HTML
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Comparations Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
                h1 {{ text-align: center; color: #4CAF50; }}
                h2 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                tr:hover {{ background-color: #ddd; }}
                p {{ line-height: 1.6; }}
            </style>
        </head>
        <body>
            <h1>Comparations Report</h1>
            <h2>Billing Period</h2>
            <p><strong>Status:</strong> {billing_period['status']}</p>
            <p><strong>Invoice Start Date:</strong> {billing_period['invoice_start_date']}</p>
            <p><strong>Invoice End Date:</strong> {billing_period['invoice_end_date']}</p>
            <p><strong>Measurement Start Date:</strong> {billing_period['measurement_start_date']}</p>
            <p><strong>Measurement End Date:</strong> {billing_period['measurement_end_date']}</p>
            <p><strong>Days Billed:</strong> {billing_period['days_billed']}</p>
            <h2>Consumption Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Invoice</th>
                        <th>Measurement</th>
                        <th>Difference</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Invoice</td>
                        <td>{consumption_details['Invoice']['invoice']}</td>
                        <td>{consumption_details['Invoice']['measurement']}</td>
                        <td>{consumption_details['Invoice']['difference']}</td>
                    </tr>
                </tbody>
            </table>
            <h2>Total Estimated</h2>
            <p><strong>Total Estimated with Time of Use:</strong> {total_estimated}</p>
        </body>
        </html>
        """

        # Generar PDF
        pdf = HTML(string=html_template).write_pdf()
        print("PDF generated successfully.")

        # Respuesta con el PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="comparations_report.pdf"'
        return response

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return Response({"error": str(e)}, status=500)
