from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from voltix.models import NotificationSettings
from .serializers import NotificationSettingsSerializer

class NotificationSettingsView(APIView):
    permission_classes = [IsAuthenticated]

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
