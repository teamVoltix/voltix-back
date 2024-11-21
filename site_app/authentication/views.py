from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from voltix.models import User, Profile
import json
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes, authentication_classes
from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view

def index(request):
    return HttpResponse("Authentication es aqui.")

def inicio(request):
    return render(request, 'auth/inicio.html')  

from rest_framework.permissions import AllowAny



# @api_view(['POST'])  # Especificas los métodos HTTP permitidos aquí
# @swagger_auto_schema(
#     operation_description="Registrar un nuevo usuario.",
#     request_body=openapi.Schema(
#         type=openapi.TYPE_OBJECT,
#         properties={
#             'fullname': openapi.Schema(type=openapi.TYPE_STRING, description="Nombre completo del usuario"),
#             'dni': openapi.Schema(type=openapi.TYPE_STRING, description="DNI del usuario"),
#             'email': openapi.Schema(type=openapi.TYPE_STRING, description="Correo electrónico del usuario"),
#             'password': openapi.Schema(type=openapi.TYPE_STRING, description="Contraseña del usuario"),
#         },
#     ),
#     responses={
#         201: openapi.Response(
#             description="Usuario registrado exitosamente",
#             schema=openapi.Schema(
#                 type=openapi.TYPE_OBJECT,
#                 properties={
#                     'message': openapi.Schema(type=openapi.TYPE_STRING),
#                     'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
#                     'fullname': openapi.Schema(type=openapi.TYPE_STRING),
#                 }
#             )
#         ),
#         400: "Bad Request",
#         500: "Internal Server Error",
#     }
# )


################################################################################################################################


################################################################################################################################
################################################# REGISTRO DE USUARIO ##########################################################
################################################################################################################################

import re  # Importar para realizar validaciones de expresiones regulares
# @api_view(['POST'])
# @csrf_exempt
# def registro_usuario(request):
#     if request.method == 'POST':
#         try:
#             # Cargar los datos del body de la solicitud
#             data = json.loads(request.body)
#             fullname = data.get('fullname')
#             dni = data.get('dni')
#             email = data.get('email')
#             password = data.get('password')

#             # Validaciones
#             if User.objects.filter(dni=dni).exists():
#                 return JsonResponse({"error": "Este DNI ya está registrado."}, status=400)

#             if not fullname or not email or not password:
#                 return JsonResponse({"error": "Todos los campos (fullname, email, password) son requeridos."}, status=400)

#             # Validación del formato del correo electrónico
#             try:
#                 validate_email(email)
#             except ValidationError:
#                 return JsonResponse({"error": "El formato del correo electrónico es inválido."}, status=400)

#             if User.objects.filter(email=email).exists():
#                 return JsonResponse({"error": "Este correo electrónico ya está registrado."}, status=400)

#             # Validación de la contraseña
#             if len(password) < 8 or len(password) > 15:
#                 return JsonResponse({"error": "La contraseña debe tener entre 8 y 15 caracteres."}, status=400)
#             if not re.search(r'[A-Z]', password):
#                 return JsonResponse({"error": "La contraseña debe tener al menos 1 letra mayúscula."}, status=400)
#             if not re.search(r'[a-z]', password):
#                 return JsonResponse({"error": "La contraseña debe tener al menos 1 letra minúscula."}, status=400)
#             if not re.search(r'[0-9]', password):
#                 return JsonResponse({"error": "La contraseña debe tener al menos 1 número."}, status=400)
#             if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
#                 return JsonResponse({"error": "La contraseña debe tener al menos 1 carácter especial."}, status=400)
#             if re.search(r'\s', password):
#                 return JsonResponse({"error": "La contraseña no debe contener espacios."}, status=400)

#             # Hashear la contraseña
#             hashed_password = make_password(password)

#             # Crear el usuario
#             user = User(
#                 fullname=fullname,
#                 dni=dni,
#                 email=email,
#                 password=hashed_password
#             )
#             user.save()
            
#             # Respuesta exitosa
#             return JsonResponse({
#                 "message": "Usuario registrado exitosamente",
#                 "user_id": user.user_id,
#                 "fullname": user.fullname,
#             }, status=201)
        
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Datos de solicitud no válidos. Asegúrate de enviar un JSON válido."}, status=400)
#         except Exception as e:
#             return JsonResponse({"error": f"Ocurrió un error: {str(e)}"}, status=500)

#     return JsonResponse({"error": "Método no permitido"}, status=405)

################################################################################################################################
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import AllowAny
class UserRegistrationView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user.",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully.",
                examples={
                    "application/json": {
                        "message": "Usuario registrado exitosamente",
                        "user_id": 1,
                        "fullname": "John Doe",
                    }
                }
            ),
            400: "Invalid input data."
        }
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


################################################################################################################################
#################################################### LOGIN DE USUARIO ##########################################################
################################################################################################################################


from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
import json



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import LoginSerializer
from django.http import JsonResponse
from rest_framework.permissions import AllowAny

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Authenticate a user using their DNI and password to retrieve JWT access and refresh tokens.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="User authenticated successfully. JWT tokens and user info are returned.",
                examples={
                    "application/json": {
                        "message": "Login successful",
                        "access_token": "JWT_ACCESS_TOKEN",
                        "refresh_token": "JWT_REFRESH_TOKEN",
                        "user_id": 1,
                        "fullname": "John Doe",
                    }
                },
            ),
            401: openapi.Response(
                description="Invalid credentials. User authentication failed.",
                examples={
                    "application/json": {"error": "Invalid credentials. Please try again."}
                },
            ),
            400: openapi.Response(
                description="Validation errors due to missing or incorrect fields.",
                examples={
                    "application/json": {
                        "dni": ["This field is required."],
                        "password": ["This field is required."],
                    }
                },
            ),
        },
    )

    def post(self, request):
        # Validate the input with serializer
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        dni = serializer.validated_data['dni']
        password = serializer.validated_data['password']

        # Authenticate the user
        user = authenticate(request, username=dni, password=password)

        if user is not None:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user_id": user.user_id,  # Change `user.user_id` if using custom fields
                "fullname": user.fullname,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials. Please try again."}, status=status.HTTP_401_UNAUTHORIZED)

################################################################################################################################

# to check the TOKEN
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": f"Hello, {request.user.fullname}! Your token is valid."})


# USER PROFILE

# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def user_profile(request):
#     user = request.user
#     return Response({
#         "user_id": user.user_id,
#         "fullname": user.fullname,
#         "email": user.email,
#         "created_at": user.created_at,
#         "updated_at": user.updated_at,
#     })



###############################################################################################################################
########################################################### LOGOUT ############################################################
###############################################################################################################################

@api_view(['POST'])
@permission_classes([IsAuthenticated])
# solo los usuarios autenticados pueden acceder a esta vista
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh_token")
        #Obtiene el refresh_token del cuerpo de la solicitud POST. Si el refresh_token no está presente, refresh_token será None
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=400)
            # Verifica si el refresh_token está presente. Si no lo está, devuelve una respuesta con un mensaje de error 
            # {"error": "Refresh token is required"} y un código de estado 400 Bad Request

        token = RefreshToken(refresh_token)
        token.blacklist()
        # Llama al método blacklist() del token para agregarlo a la lista negra. Esto significa que el refresh_token 
        # será invalidado y no podrá ser usado nuevamente para obtener un nuevo access_token. Nota: Para que esta operación 
        # funcione, debes tener habilitada la lista negra en tu proyecto ('rest_framework_simplejwt.token_blacklist' debe estar
        #  en INSTALLED_APPS y las migraciones aplicadas).
        return Response({"message": "Successfully logged out"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
################################################################################################################################


################################################################################################################################
#################################### CHANGE PASSWORD CON ENVIO DE EMAIL DE NOTIFICACION ########################################
################################################################################################################################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ChangePasswordSerializer
from django.core.mail import send_mail
from voltix.models import User  # Importa el modelo User

class change_password_view(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Cambiar la contraseña del usuario autenticado
            serializer.update_password()

            # Obtener el correo electrónico del usuario autenticado
            user = request.user  # Usuario autenticado
            user_email = user.email  # Obtener el correo del usuario desde el modelo

            # Enviar el correo de notificación
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
                    from_email='voltix899@gmail.com',  # Correo remitente configurado en settings.py
                    recipient_list=[user_email],  # Lista con el correo del usuario
                    fail_silently=False,  # Si hay un error, lanza una excepción
                )
            except Exception as e:
                # Manejar errores durante el envío del correo
                print(f"Error al enviar el correo: {e}")

            # Responder con éxito
            return Response({"detail": "La contraseña ha sido cambiada exitosamente y se ha enviado un correo de notificación."}, status=status.HTTP_200_OK)

        # Si los datos son inválidos, devolver errores
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

################################################################################################################################


################################################################################################################################
############################################# PASSWORD RESET - PEDIDO CON EMAIL ################################################
################################################################################################################################

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
import json
import os

User = get_user_model()

@csrf_exempt
def password_reset_request_view(request):
    if request.method == 'POST':
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
                f"Hola {user.fullname},\n\n"  # Cambiado de get_full_name a fullname
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
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)

################################################################################################################################


################################################################################################################################
########################################## PASSWORD RESET - NUEVA PASSWORD #####################################################
################################################################################################################################

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
import json
import os


@csrf_exempt
def password_reset_view(request, uidb64, token):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not new_password or not confirm_password:
            return JsonResponse({"error": "Ambas contraseñas son requeridas."}, status=400)

        if new_password != confirm_password:
            return JsonResponse({"error": "Las contraseñas no coinciden."}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return JsonResponse({"detail": "Tu contraseña ha sido restablecida exitosamente."}, status=200)
        else:
            return JsonResponse({"error": "El enlace de restablecimiento no es válido o ha expirado."}, status=400)
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)

################################################################################################################################