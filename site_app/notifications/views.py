from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers  # Importamos serializers
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
                "enable_alerts": True,
                "enable_recommendations": False,
                "enable_reminders": True,
            },
        ),
        responses={
            200: openapi.Response(
                description="Configuración actualizada exitosamente.",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Configuración actualizada exitosamente.",
                        "data": {
                            "enable_alerts": True,
                            "enable_recommendations": False,
                            "enable_reminders": True,
                        },
                    }
                },
            ),
            400: openapi.Response(
                description="Datos inválidos.",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Datos inválidos.",
                        "errors": {
                            "enable_alerts": ["Este campo es obligatorio."],
                        },
                    }
                },
            ),
            500: openapi.Response(
                description="Error interno del servidor.",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Error al procesar la solicitud.",
                        "details": "Detalles del error...",
                    }
                },
            ),
        },
    )
    def post(self, request):
        user = request.user
        try:
            # Asegurarnos de que solo exista una configuración por usuario
            settings_queryset = NotificationSettings.objects.filter(user=user)
            if settings_queryset.count() > 1:
                # Si hay duplicados, eliminamos todos menos el primero
                settings_queryset.exclude(pk=settings_queryset.first().pk).delete()

            # Obtenemos o creamos la configuración
            settings, created = NotificationSettings.objects.get_or_create(user=user)
            serializer = NotificationSettingsSerializer(settings, data=request.data, partial=True)

            # Validar cantidad de campos
            max_allowed_fields = 3  # Número máximo de campos permitidos
            if len(request.data.keys()) > max_allowed_fields:
                return Response(
                    {
                        "status": "error",
                        "message": f"Demasiados campos. Se permiten hasta {max_allowed_fields} campos.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validar los datos del serializer
            if not serializer.is_valid():
                return Response(
                    {
                        "status": "error",
                        "message": "Datos inválidos.",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Guardar la configuración actualizada
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Configuración actualizada exitosamente.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except serializers.ValidationError as ve:
            # Manejar errores de validación explícitamente
            return Response(
                {
                    "status": "error",
                    "message": "Error de validación en el payload.",
                    "errors": ve.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            # Manejar errores generales y registrar para depuración
            print(f"Error en NotificationSettingsView: {e}")
            return Response(
                {
                    "status": "error",
                    "message": "Error al procesar la solicitud.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
