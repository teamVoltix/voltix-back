from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from voltix.models import Profile
from datetime import date
from django.core.exceptions import ValidationError

# Endpoint para obtener el perfil del usuario (GET)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    try:
        # Intentar obtener el perfil asociado al usuario
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # Si no existe, creamos un perfil con valores predeterminados
        profile = Profile.objects.create(
            user=request.user,
            birth_date=None,
            address="",
            phone_number="",
            preferences={}
        )

    # Preparar los datos de respuesta
    profile_data = {
        'fullname': request.user.fullname,
        'email': request.user.email,
        'birth_date': profile.birth_date,
        'address': profile.address,
        'phone_number': profile.phone_number,
        'preferences': profile.preferences,
    }

    return Response(profile_data)

# Endpoint para actualizar parcialmente el perfil del usuario (PATCH)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def patch_profile(request):
    try:
        # Intentar obtener el perfil asociado al usuario
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # Si no existe el perfil, devolver un error
        return Response({"error": "El perfil no existe."}, status=status.HTTP_404_NOT_FOUND)

    # Extraer los datos del cuerpo de la solicitud
    data = request.data

    # Actualizar solo los campos permitidos
    allowed_fields = ['birth_date', 'address', 'phone_number', 'preferences']
    updated_fields = {}

    for field in allowed_fields:
        if field in data:
            try:
                setattr(profile, field, data[field])
                updated_fields[field] = data[field]
            except ValidationError as e:
                return Response({f"error_{field}": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Guardar los cambios en el perfil
    profile.save()

    return Response({
        "message": "Perfil actualizado exitosamente.",
        "updated_fields": updated_fields
    }, status=status.HTTP_200_OK)
