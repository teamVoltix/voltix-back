from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserRegistrationSerializer, LoginSerializer, ChangePasswordSerializer
import json
import os


User = get_user_model()

# ==========================================================
# General Views
# ==========================================================

def index(request):
    """Basic view to verify the API is running."""
    return HttpResponse("Authentication es aqui.")

def inicio(request):
    """Renders a sample HTML page."""
    return render(request, 'auth/inicio.html')

# ==========================================================
# User Registration
# ==========================================================

class UserRegistrationView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user.",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully.",
                examples={"application/json": {
                    "message": "Usuario registrado exitosamente",
                    "user_id": 1,
                    "fullname": "John Doe",
                }}
            ),
            400: "Invalid input data.",
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Usuario registrado exitosamente",
                "user_id": user.id,
                "fullname": user.fullname,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==========================================================
# User Login
# ==========================================================

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Authenticate a user using their DNI and password to retrieve JWT access and refresh tokens.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="User authenticated successfully.",
                examples={"application/json": {
                    "message": "Login successful",
                    "access_token": "JWT_ACCESS_TOKEN",
                    "refresh_token": "JWT_REFRESH_TOKEN",
                    "user_id": 1,
                    "fullname": "John Doe",
                }}
            ),
            401: openapi.Response(description="Invalid credentials."),
            400: openapi.Response(description="Validation errors."),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        dni = serializer.validated_data['dni']
        password = serializer.validated_data['password']

        user = authenticate(request, username=dni, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user_id": user.user_id,
                "fullname": user.fullname,
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials. Please try again."}, status=status.HTTP_401_UNAUTHORIZED)

# ==========================================================
# Token Verification
# ==========================================================

@swagger_auto_schema(
    method="get",
    operation_summary="Protected View",
    operation_description="Verify the validity of the JWT token and retrieve a personalized message for the user.",
    responses={
        200: openapi.Response(description="Token is valid."),
        401: openapi.Response(description="Unauthorized."),
    },
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": f"Hello, {request.user.fullname}! Your token is valid."})

# ==========================================================
# User Logout
# ==========================================================

@swagger_auto_schema(
    method="post",
    operation_summary="User Logout",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["refresh_token"],
        properties={
            "refresh_token": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The refresh token to be blacklisted."
            ),
        },
    ),
    responses={
        200: openapi.Response(description="Successfully logged out."),
        400: openapi.Response(description="Invalid refresh token."),
        500: openapi.Response(description="Server error."),
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get("refresh_token")
    if not refresh_token:
        return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
    except Exception as e:
        # Cambiar el código a 400
        return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

# ==========================================================
# Change Password
# ==========================================================

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Change Password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["old_password", "new_password", "confirm_new_password"],
            properties={
                "old_password": openapi.Schema(type=openapi.TYPE_STRING),
                "new_password": openapi.Schema(type=openapi.TYPE_STRING),
                "confirm_new_password": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(description="Password changed successfully."),
            400: openapi.Response(description="Validation errors."),
            500: openapi.Response(description="Error while sending email."),
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.update_password()

            user = request.user
            user_email = user.email

            try:
                send_mail(
                    subject='Notificación de cambio de contraseña',
                    message=(
                        f'Hola {user.fullname},\n\n'
                        'Queremos informarte que tu contraseña ha sido cambiada exitosamente.\n'
                        'Si no realizaste este cambio, por favor contacta con nuestro equipo de soporte de inmediato.\n\n'
                        'Saludos,\n'
                        'El equipo de Voltix'
                    ),
                    from_email='voltix899@gmail.com',
                    recipient_list=[user_email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error al enviar el correo: {e}")

            return Response({"detail": "La contraseña ha sido cambiada exitosamente y se ha enviado un correo de notificación."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==========================================================
# Password Reset Request
# ==========================================================

@swagger_auto_schema(
    method="post",
    operation_summary="Password Reset Request",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["email"],
        properties={"email": openapi.Schema(type=openapi.TYPE_STRING)},
    ),
    responses={
        200: openapi.Response(description="Reset link sent."),
        400: openapi.Response(description="Missing or invalid email."),
        404: openapi.Response(description="User not found."),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])  # Permitir acceso sin autenticación
@csrf_exempt
def password_reset_request_view(request):
    data = json.loads(request.body)
    email = data.get('email')
    if not email:
        return JsonResponse({"error": "El email es requerido."}, status=400)

    user = get_object_or_404(User, email=email)
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_link = f"{os.getenv('BACKEND_URL')}/password/reset/{uid}/{token}/"

    send_mail(
        subject='Restablecimiento de contraseña',
        message=(
            f"Hola {user.fullname},\n\n"
            "Recibimos una solicitud para restablecer tu contraseña. "
            "Haz clic en el siguiente enlace para establecer una nueva contraseña:\n\n"
            f"{reset_link}\n\n"
            "Si no realizaste esta solicitud, puedes ignorar este correo."
        ),
        from_email='voltix899@gmail.com',
        recipient_list=[email],
        fail_silently=False,
    )

    return JsonResponse({"detail": "Se ha enviado un correo con el enlace para restablecer tu contraseña."}, status=200)

# ==========================================================
# Password Reset Confirmation
# ==========================================================

@swagger_auto_schema(
    method="post",
    operation_summary="Password Reset",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["new_password", "confirm_password"],
        properties={
            "new_password": openapi.Schema(type=openapi.TYPE_STRING),
            "confirm_password": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={
        200: openapi.Response(description="Password reset successfully."),
        400: openapi.Response(description="Invalid token or mismatched passwords."),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])  # Permitir acceso sin autenticación
@csrf_exempt
def password_reset_view(request, uidb64, token):
    data = json.loads(request.body)
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not new_password or not confirm_password:
        return JsonResponse({"error": "Ambas contraseñas son requeridas."}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return JsonResponse({"error": "Las contraseñas no coinciden."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return JsonResponse({"detail": "Tu contraseña ha sido restablecida exitosamente."}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"error": "El enlace de restablecimiento no es válido o ha expirado."}, status=status.HTTP_400_BAD_REQUEST)