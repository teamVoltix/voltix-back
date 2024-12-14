from rest_framework import serializers
from apps.voltix.models import NotificationSettings

class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = ['enable_alerts', 'enable_recommendations', 'enable_reminders']

    def validate(self, data):
        """
        Validar que el payload contenga solo los campos permitidos.
        """
        allowed_keys = {'enable_alerts', 'enable_recommendations', 'enable_reminders'}
        invalid_keys = set(self.initial_data.keys()) - allowed_keys
        if invalid_keys:
            raise serializers.ValidationError({
                "invalid_fields": f"Campos inválidos: {', '.join(invalid_keys)}"
            })
        return data