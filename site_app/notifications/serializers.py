from rest_framework import serializers
from voltix.models import NotificationSettings

class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = ['enable_alerts', 'enable_recommendations', 'enable_reminders']
