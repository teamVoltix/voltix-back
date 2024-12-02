from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
from rest_framework.decorators import api_view  # Import necesario
from voltix.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from datetime import timezone

def index(request):
    return HttpResponse("Bienvenido a Users.")

@swagger_auto_schema(
    method='get',
    operation_summary="Get All Users",
    operation_description="Retrieve a list of all users in the system, including their user ID, full name, DNI, email, and timestamps.",
    responses={
        200: openapi.Response(
            description="List of users retrieved successfully.",
            examples={
                "application/json": {
                    "message": "Usuarios obtenidos exitosamente",
                    "usuarios": [
                        {
                            "user_id": 1,
                            "fullname": "John Doe",
                            "dni": "12345678A",
                            "email": "johndoe@example.com",
                            "created_at": "2024-11-21T12:00:00Z",
                            "updated_at": "2024-11-21T12:00:00Z"
                        },
                        {
                            "user_id": 2,
                            "fullname": "Jane Smith",
                            "dni": "87654321B",
                            "email": "janesmith@example.com",
                            "created_at": "2024-11-22T12:00:00Z",
                            "updated_at": "2024-11-22T12:00:00Z"
                        }
                    ]
                }
            }
        ),
        500: openapi.Response(
            description="Server error while retrieving users.",
            examples={
                "application/json": {
                    "error": "Ocurrió un error: Error message"
                }
            }
        ),
        405: openapi.Response(
            description="Method not allowed.",
            examples={
                "application/json": {
                    "error": "Método no permitido"
                }
            }
        ),
    }
)
@api_view(['GET'])
@csrf_exempt
@permission_classes([AllowAny])
def get_all_users(request):
    if request.method == 'GET':
        try:
            # Obtener todos los usuarios ordenados por created_at ascendente
            users = User.objects.all().order_by('created_at').values(
                'user_id', 'fullname', 'dni', 'email', 'created_at', 'updated_at'
            )
            users_list = [
                {
                    **user,
                    "created_at": user['created_at'].astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
                    "updated_at": user['updated_at'].astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
                }
                for user in users
            ]

            return JsonResponse({
                "message": "Usuarios obtenidos exitosamente",
                "usuarios": users_list
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": f"Ocurrió un error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)
