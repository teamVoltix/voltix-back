from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from voltix.models import Profile
from datetime import date

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
