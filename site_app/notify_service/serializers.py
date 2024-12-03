from rest_framework import serializers
from voltix.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    notification_type = serializers.CharField(source='type')  # Mapea el campo 'type' como 'notification_type'

    class Meta:
        model = Notification
        fields = ['title', 'message', 'notification_type']  # Usa 'notification_type' en lugar de 'type'

    def get_title(self, obj):
        return obj.message[:50]