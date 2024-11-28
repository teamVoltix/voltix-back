from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from voltix.models import NotificationSettings
from .serializers import NotificationSettingsSerializer

class NotificationSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Actualizar configuración de notificaciones",
        operation_description="""
            Permite a un usuario autenticado actualizar o crear su configuración de notificaciones. 
            Si no existe una configuración previa, se crea una nueva asociada al usuario.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            additional_properties=True,
            description="Cuerpo de la solicitud con las configuraciones a actualizar o crear.",
            example={
                "key1": "value1",
                "key2": "value2"
            }
        ),
        responses={
            200: openapi.Response(
                description="Configuración actualizada exitosamente.",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Configuración actualizada exitosamente.",
                        "data": {
                            "key1": "value1",
                            "key2": "value2"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Datos inválidos.",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Datos inválidos.",
                        "errors": {
                            "key1": ["Este campo es obligatorio."]
                        }
                    }
                }
            ),
            500: openapi.Response(
                description="Error interno del servidor.",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Error al procesar la solicitud.",
                        "details": "Detalles del error..."
                    }
                }
            )
        }
    )
    def post(self, request):
        user = request.user
        try:
            # Obtener o crear la configuración de notificaciones del usuario
            settings, created = NotificationSettings.objects.get_or_create(user=user)
            
            # Serializar los datos enviados en la solicitud
            serializer = NotificationSettingsSerializer(settings, data=request.data, partial=True)
            
            # Validar y guardar los cambios
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "Configuración actualizada exitosamente.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                "status": "error",
                "message": "Datos inválidos.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "Error al procesar la solicitud.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
