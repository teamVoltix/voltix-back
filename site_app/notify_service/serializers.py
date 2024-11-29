from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    # Añadir un campo 'title' calculado
    title = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['title', 'message']  # Especificamos solo los campos que necesitamos

    def get_title(self, obj):
        # Aquí puedes devolver el valor que quieras para el campo 'title'
        # Usamos los primeros 50 caracteres del mensaje como título
        return obj.message[:50]  # Usar los primeros 50 caracteres del mensaje como título
