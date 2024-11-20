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

@csrf_exempt
def registro_usuario(request):
    if request.method == 'POST':
        try:
            # Cargar los datos del body de la solicitud
            data = json.loads(request.body)
            fullname = data.get('fullname')
            dni = data.get('dni')
            email = data.get('email')
            password = data.get('password')

            # Validaciones
            if User.objects.filter(dni=dni).exists():
                return JsonResponse({"error": "Este DNI ya está registrado."}, status=400)

            if not fullname or not email or not password:
                return JsonResponse({"error": "Todos los campos (fullname, email, password) son requeridos."}, status=400)

            # Validación del formato del correo electrónico
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({"error": "El formato del correo electrónico es inválido."}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({"error": "Este correo electrónico ya está registrado."}, status=400)
                
            # Hashear la contraseña
            hashed_password = make_password(password)

            # Crear el usuario
            user = User(
                fullname=fullname,
                dni=dni,
                email=email,
                password=hashed_password
            )
            user.save()
            
            # Create the profile for the new user
            # Profile.objects.create(user=user)

            print("Usuario registrado")

            # Respuesta exitosa
            return JsonResponse({
                "message": "Usuario registrado exitosamente",
                "user_id": user.user_id,
                "fullname": user.fullname,
            }, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos de solicitud no válidos. Asegúrate de enviar un JSON válido."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Ocurrió un error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            dni = data.get('dni')
            password = data.get('password')

            # Validate input
            if not dni or not password:
                return JsonResponse({"error": "DNI and password are required."}, status=400)

            # Authenticate the user
            user = authenticate(request, username=dni, password=password)

            if user is not None:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    "message": "Login successful",
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user_id": user.user_id,
                    "fullname": user.fullname,
                }, status=200)
            else:
                return JsonResponse({"error": "Invalid credentials. Please try again."}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid request data. Ensure it's valid JSON."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Method not allowed."}, status=405)

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
    
    ###########################################################################################################################

################################################################################################################################
################################################# CHANGE PASSWORD ##############################################################
################################################################################################################################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ChangePasswordSerializer

class change_password_view(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.update_password()
            return Response({"detail": "La contraseña ha sido cambiada exitosamente."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

###############################################################################################################################