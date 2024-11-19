from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from voltix.models import Profile
from rest_framework.decorators import permission_classes, authentication_classes
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@login_required
@permission_classes([IsAuthenticated])

def profile_view(request):
    # Get the profile associated with the logged-in user
    profile = get_object_or_404(Profile, user=request.user)
    
    # Prepare the response data
    profile_data = {
        'fullname': profile.user.fullname,
        'email': profile.user.email,
        'birth_date': profile.birth_date,
        'address': profile.address,
        'phone_number': profile.phone_number,
        'preferences': profile.preferences,
    }
    
    return JsonResponse(profile_data)
