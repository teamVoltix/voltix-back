from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .login_serializer import LoginSerializer
from .logging_config import logger

class LoginView(APIView):
    """
    Endpoint for user login using DNI and password.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            # Generate tokens
            user = serializer.validated_data['user']
            tokens = serializer.create_tokens(user)
            return Response(tokens, status=status.HTTP_200_OK)

        # Log invalid login attempts
        logger.warning(f"Invalid login attempt: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
