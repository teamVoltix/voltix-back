from rest_framework import serializers
from apps.general.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    notification_type = serializers.CharField(source='type')

    class Meta:
        model = Notification
        fields = ['title', 'message', 'notification_type', 'created_at'] 

    def get_title(self, obj):
        return obj.message[:50]