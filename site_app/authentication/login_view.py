from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from voltix.models import Token
from django.utils.timezone import now
from datetime import timedelta

class LoginView(APIView):
    def post(self, request):
        # Aquí asumes que ya validaste las credenciales del usuario
        user = request.user

        # Generar un nuevo token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Guardar el token en la base de datos
        token = Token.objects.create(
            user=user,
            token=access_token,
            expires_at=now() + timedelta(days=7)  # Establece una duración para el token
        )

        return Response({
            "refresh": str(refresh),
            "access": access_token,
        }, status=status.HTTP_200_OK)
