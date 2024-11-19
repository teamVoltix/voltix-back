from rest_framework import serializers
from django.contrib.auth.models import User

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual no es correcta.")
        return value

    def validate_new_password(self, value):
        # Puedes agregar validaciones adicionales aquí para la nueva contraseña
        if len(value) < 8:
            raise serializers.ValidationError("La nueva contraseña debe tener al menos 8 caracteres.")
        return value

    def update_password(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()