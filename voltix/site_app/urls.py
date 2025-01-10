from django.contrib import admin
from django.urls import path, include
from apps.general.views import index
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse
import httpx  # Usaremos httpx para llamar al microservicio

# Definimos una función que llama al microservicio voltix-reporte
def download_report(request):
    comparison_id = request.GET.get('id')  # Obtiene el ID de comparación desde los parámetros de la URL
    user = request.user.username  # Simula el usuario autenticado
    if not comparison_id:
        return HttpResponse("ID de comparación requerido", status=400)

    try:
        # Llama al microservicio voltix-reporte
        url = "http://localhost:8000/download_report"  # Cambia esto si voltix-reporte está en un servidor diferente
        params = {"id": comparison_id, "user": user}
        response = httpx.get(url, params=params)

        if response.status_code == 200:
            # Devuelve el PDF como respuesta HTTP
            pdf_content = response.content
            resp = HttpResponse(pdf_content, content_type="application/pdf")
            resp["Content-Disposition"] = "attachment; filename=report.pdf"
            return resp
        else:
            return HttpResponse(f"Error {response.status_code}: {response.text}", status=response.status_code)

    except Exception as e:
        return HttpResponse(f"Error al generar el reporte: {str(e)}", status=500)

schema_view = get_schema_view(
   openapi.Info(
      title="Voltix API",
      default_version='v1',
      description="Documentación de la API para Voltix",
      terms_of_service="https://example.com/terms/",  # Enlace pendiente de definir
      contact=openapi.Contact(email="voltix899@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),  # Permitir acceso a todos
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),  # La ruta actual de voltix
    path("api/auth/", include("apps.authentication.urls")),
    path('api/profile/', include('apps.userprofile.urls')),
    path('users/', include('apps.users.urls')),
    path("api/invoices/", include("apps.invoices.urls")),
    path('api/measurements/', include('apps.measurements.urls')),
    path('comparations/', include('apps.comparations.urls')),
    # Cambiamos la referencia de pdf_measurement a la nueva función que llama al microservicio
    path('api/measurements/report/download/', download_report, name='download_report'),
    #notifications
    path('api/notifications/general/', include('apps.notifications.urls')),
    path('api/notifications/service/', include('apps.notify_service.urls')),   
    # Rutas de Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redocs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Ruta de Tesseract
    path('tesseract/', include('apps.tesseract.urls')),
]
