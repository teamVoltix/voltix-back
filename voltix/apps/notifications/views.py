from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers  # Importamos serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.general.models import NotificationSettings
from .serializers import NotificationSettingsSerializer

class NotificationSettingsRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    """
    API to retrieve notification settings for the authenticated user.
    """

    def get(self, request):
        try:
            settings = NotificationSettings.objects.get(user=request.user)
            serializer = NotificationSettingsSerializer(settings)
            return Response(
                {
                    "status": "success",
                    "message": "Configuración recuperada exitosamente.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except NotificationSettings.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Configuración de notificaciones no encontrada.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

class NotificationSettingsUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    """
    API to update or create notification settings for the authenticated user.
    """

    def post(self, request):
        user = request.user
        try:
            # Ensure only one configuration exists per user
            settings_queryset = NotificationSettings.objects.filter(user=user)
            if settings_queryset.count() > 1:
                # If duplicates exist, delete all but the first
                settings_queryset.exclude(pk=settings_queryset.first().pk).delete()

            # Retrieve or create the user's settings
            settings, created = NotificationSettings.objects.get_or_create(user=user)
            serializer = NotificationSettingsSerializer(settings, data=request.data, partial=True)

            # Validate the data
            if not serializer.is_valid():
                return Response(
                    {
                        "status": "error",
                        "message": "Datos inválidos.",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Save the updated configuration
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
            return Response(
                {
                    "status": "error",
                    "message": "Error de validación en el payload.",
                    "errors": ve.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "Error al procesar la solicitud.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
