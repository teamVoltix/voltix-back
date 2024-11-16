from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from voltix.models import Usuario, Perfil
import json
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes, authentication_classes











from django.http import HttpResponse


def index(request):
    return HttpResponse("Authentication es aqui.")

def inicio(request):
    return render(request, 'auth/inicio.html')  

# Endponit de registro desde linia 31 a la 85 aprox.
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
            if Usuario.objects.filter(dni=dni).exists():
                return JsonResponse({"error": "Este DNI ya está registrado."}, status=400)

            if not fullname or not email or not password:
                return JsonResponse({"error": "Todos los campos (fullname, email, password) son requeridos."}, status=400)

            # Validación del formato del correo electrónico
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({"error": "El formato del correo electrónico es inválido."}, status=400)

            if Usuario.objects.filter(email=email).exists():
                return JsonResponse({"error": "Este correo electrónico ya está registrado."}, status=400)
                
            # Hashear la contraseña
            hashed_password = make_password(password)

            # Crear el usuario
            usuario = Usuario(
                fullname=fullname,
                dni=dni,
                email=email,
                password=hashed_password
            )
            usuario.save()

            print("Usuario registrado")

            # Respuesta exitosa
            return JsonResponse({
                "message": "Usuario registrado exitosamente",
                "user_id": usuario.user_id,
                "fullname": usuario.fullname,
            }, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos de solicitud no válidos. Asegúrate de enviar un JSON válido."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Ocurrió un error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)
