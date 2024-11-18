from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from voltix.models import Usuario


class LoginSerializer(serializers.Serializer):
    dni = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        dni = data.get('dni')
        password = data.get('password')

        try:
            user = Usuario.objects.get(dni=dni)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({"dni": "DNI no encontrado."})


        if not check_password(password, user.password):
            raise serializers.ValidationError({"password": "Contraseña incorrecta."})

        data['user'] = user
        return data

    def create_tokens(self, user):
        # SimpleJWT
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'fullname': user.fullname,
            'email': user.email,
        }

