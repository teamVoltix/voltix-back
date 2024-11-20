from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
import re

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        # Verificar longitud
        if len(value) < 8 or len(value) > 15:
            raise ValidationError("La contraseña debe tener entre 8 y 15 caracteres.")
        
        # Verificar que tenga al menos una letra mayúscula
        if not re.search(r'[A-Z]', value):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        # Verificar que tenga al menos una letra minúscula
        if not re.search(r'[a-z]', value):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
        
        # Verificar que tenga al menos un número
        if not re.search(r'\d', value):
            raise ValidationError("La contraseña debe contener al menos un número.")
        
        # Verificar que tenga al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")
        
        return value

    def validate(self, data):
        # Validar que las contraseñas coincidan
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Las contraseñas no coinciden."})
        
        # Validar la contraseña antigua
        user = self.context['request'].user
        if not check_password(data.get('old_password'), user.password):
            raise serializers.ValidationError({"old_password": "La contraseña actual es incorrecta."})
        
        return data

    def update_password(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()