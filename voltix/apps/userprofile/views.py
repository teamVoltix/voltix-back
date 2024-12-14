from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.voltix.models import Profile
from datetime import date
from django.core.exceptions import ValidationError
from cloudinary.uploader import upload, destroy
from cloudinary.exceptions import Error as CloudinaryError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from PIL import Image
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import datetime
from apps.voltix.utils.upload_cloudinary import process_and_upload_image



# Endpoint para obtener el perfil del usuario (GET)
@swagger_auto_schema(
    method='get',
    operation_summary="Retrieve User Profile",
    operation_description="Fetches the profile information of the authenticated user. If the profile does not exist, it will be created with default values.",
    responses={
        200: openapi.Response(
            description="User profile retrieved successfully.",
            examples={
                "application/json": {
                    "fullname": "John Doe",
                    "email": "john.doe@example.com",
                    "birth_date": None,
                    "address": "",
                    "phone_number": "",
                    "photo": ""
                }
            }
        ),
        401: openapi.Response(
            description="Unauthorized. User not authenticated.",
            examples={
                "application/json": {
                    "detail": "Authentication credentials were not provided."
                }
            },
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(
            user=request.user,
            birth_date=None,
            address="",
            phone_number="",
            photo_url=""
        )

    profile_data = {
        'fullname': request.user.fullname,
        'dni': request.user.dni,
        'email': request.user.email,
        'birth_date': profile.birth_date,
        'address': profile.address,
        'phone_number': profile.phone_number,
        'photo': profile.photo_url, 
    }

    return Response(profile_data)

# Endpoint para actualizar parcialmente el perfil del usuario (PATCH)
@swagger_auto_schema(
    method='patch',
    operation_summary="Update User Profile",
    operation_description=(
        "Allows the authenticated user to update specific fields in their profile. "
        "Only the following fields can be updated: `birth_date`, `address`, `phone_number`, `preferences`."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "birth_date": openapi.Schema(
                type=openapi.TYPE_STRING,
                format="date",
                description="The user's date of birth in YYYY-MM-DD format."
            ),
            "address": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The user's address."
            ),
            "phone_number": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="The user's phone number."
            ),
            "preferences": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="User preferences as a dictionary."
            ),
        },
        example={
            "birth_date": "1990-01-01",
            "address": "123 Main Street",
            "phone_number": "+1234567890",
            "photo": ""
        }
    ),
    responses={
        200: openapi.Response(
            description="Profile updated successfully.",
            examples={
                "application/json": {
                    "message": "Perfil actualizado exitosamente.",
                    "updated_fields": {
                        "birth_date": "1990-01-01",
                        "address": "123 Main Street"
                    }
                }
            }
        ),
        400: openapi.Response(
            description="Validation error in one or more fields.",
            examples={
                "application/json": {
                    "error_birth_date": "Invalid date format."
                }
            }
        ),
        404: openapi.Response(
            description="Profile not found.",
            examples={
                "application/json": {
                    "error": "El perfil no existe."
                }
            }
        ),
        401: openapi.Response(
            description="Unauthorized. User not authenticated.",
            examples={
                "application/json": {
                    "detail": "Authentication credentials were not provided."
                }
            }
        ),
    }
)





@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def patch_profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return Response({"error": "El perfil no existe."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    if not data:
        return Response(
            {"error": "No data provided."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    allowed_fields = ['birth_date', 'address', 'phone_number', 'photo']
    updated_fields = {}

    # Validar campos en el request
    for field in data.keys():
        if field not in allowed_fields:
            return Response(
                {"error_invalid_field": f"Field '{field}' is not allowed."},  # Cambiado para que coincida con el test
                status=status.HTTP_400_BAD_REQUEST
            )

    # Actualizar los campos permitidos
    for field in allowed_fields:
        if field in data:
            try:
                setattr(profile, field, data[field])
                updated_fields[field] = data[field]
            except ValidationError as e:
                return Response({f"error_{field}": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    profile.save()

    return Response({
        "message": "Perfil actualizado exitosamente.",
        "updated_fields": updated_fields
    }, status=status.HTTP_200_OK)





from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cloudinary.uploader import upload
from cloudinary.exceptions import Error as CloudinaryError

@swagger_auto_schema(
    method="post",
    operation_summary="Subir foto de perfil",
    operation_description="""
        Permite a un usuario autenticado subir una foto de perfil. 
        La imagen se almacena en Cloudinary, y la URL resultante se guarda en el perfil del usuario.
    """,
    manual_parameters=[
        openapi.Parameter(
            name="photo",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            description="El archivo de imagen que se subirá como foto de perfil.",
        ),
    ],
    responses={
        200: openapi.Response(
            description="Foto subida exitosamente.",
            examples={
                "application/json": {
                    "message": "Foto subida exitosamente.",
                    "photo_url": "https://res.cloudinary.com/example/profiles/photo.jpg"
                }
            },
        ),
        400: openapi.Response(
            description="Solicitud inválida.",
            examples={
                "application/json": {
                    "error": "No se encontró un archivo para subir."
                }
            },
        ),
        404: openapi.Response(
            description="Perfil no encontrado.",
            examples={
                "application/json": {
                    "error": "El perfil no existe."
                }
            },
        ),
        500: openapi.Response(
            description="Error interno del servidor.",
            examples={
                "application/json": {
                    "error": "Error de Cloudinary: Detalle del error..."
                }
            },
        ),
    }
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_profile_photo(request):
    try:
        # Obtener el perfil del usuario autenticado
        profile = Profile.objects.get(user=request.user)

        if 'photo' not in request.FILES:
            return Response({"error": "No se encontró un archivo para subir."}, status=400)

        photo = request.FILES['photo']

        try:
            # Eliminar la imagen anterior de Cloudinary (si existe)
            if profile.photo_url:
                public_id = profile.photo_url.split('/')[-1].split('.')[0]  # Extraer el public_id de la URL
                destroy(public_id)  # Elimina la imagen anterior en Cloudinary

            # Validar, procesar y subir la nueva imagen
            # Aquí llamamos a la función `process_and_upload_image`
            photo_url = process_and_upload_image(photo)

            # Actualizar el perfil con la URL de la nueva foto
            profile.photo_url = photo_url
            profile.save()

            return Response({
                "message": "Foto subida exitosamente.",
                "photo_url": photo_url
            }, status=200)

        except ValueError as e:  # Errores de validación o procesamiento
            return Response({"error": str(e)}, status=400)
        except CloudinaryError as e:  # Errores específicos de Cloudinary
            return Response({"error": f"Error de Cloudinary: {str(e)}"}, status=500)

    except Profile.DoesNotExist:
        return Response({"error": "El perfil no existe."}, status=404)

    except Exception as e:  # Cualquier otro error no manejado
        return Response({"error": f"Error inesperado: {str(e)}"}, status=500)


