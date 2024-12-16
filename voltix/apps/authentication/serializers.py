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


from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
import re
from apps.general.models import User  # Ensure User is your custom model or default Django User model

class UserRegistrationSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(max_length=255)
    dni = serializers.CharField(
        max_length=9,  # Cambiado a un máximo de 9 caracteres
        error_messages={
            "max_length": "El DNI no puede tener más de 9 caracteres."
        }
    )
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, max_length=15)

    class Meta:
        model = User
        fields = ['fullname', 'dni', 'email', 'password']


    def validate_dni(self, value):
        # Validar longitud exacta de 9 caracteres
        if len(value) != 9:
            raise serializers.ValidationError("El DNI debe tener exactamente 9 caracteres.")

        # Validar si comienza con un número
        if value[0].isdigit():
            # Validar el patrón específico: 8 números seguidos de 1 letra
            if not re.match(r"^\d{8}[A-Za-z]$", value):
                raise serializers.ValidationError(
                    "El DNI que comienza con un número debe tener 8 números seguidos de 1 letra (ejemplo: 12345678A)."
                )

        # Validar si comienza con una letra
        elif value[0].isalpha():
            # Validar el patrón específico: 1 letra, 7 números, 1 letra
            if not re.match(r"^[A-Za-z]\d{7}[A-Za-z]$", value):
                raise serializers.ValidationError(
                    "El DNI que comienza con una letra debe tener 1 letra al inicio, seguido de 7 números y 1 letra al final (ejemplo: A1234567B)."
                )
        else:
            raise serializers.ValidationError(
                "El DNI debe comenzar con una letra o un número."
            )

        # Validar que no se haya registrado previamente
        if User.objects.filter(dni=value).exists():
            raise serializers.ValidationError("Este DNI ya está registrado.")
        
        return value








    def validate_password(self, value):
        if len(value) < 8 or len(value) > 15:
            raise serializers.ValidationError("La contraseña debe tener entre 8 y 15 caracteres.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("La contraseña debe tener al menos 1 letra mayúscula.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("La contraseña debe tener al menos 1 letra minúscula.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("La contraseña debe tener al menos 1 número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("La contraseña debe tener al menos 1 carácter especial.")
        if re.search(r'\s', value):
            raise serializers.ValidationError("La contraseña no debe contener espacios.")
        return value

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    dni = serializers.CharField(
        required=True,
        max_length=20,
        help_text="The DNI (unique identifier) of the user.",
        error_messages={
            "required": "DNI is required.",
            "max_length": "DNI cannot exceed 20 characters.",
        },
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="The password associated with the user account.",
        error_messages={
            "required": "Password is required.",
        },
    )

    def validate_dni(self, value):
        # Eliminar espacios en blanco antes de validar
        return value.strip()
