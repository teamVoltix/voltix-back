from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomTokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validation
            old_token = RefreshToken(refresh_token)
            
            #uf!!!!
            user_id = old_token['user_id']
            user = User.objects.get(user_id=user_id)


            # Generation
            new_refresh_token = RefreshToken.for_user(user)
            new_access_token = str(new_refresh_token.access_token)

            # optional, pero tenemos en drf_settings.py despues de rotation --> a blacklist
            # old_token.blacklist()

            return Response({
                "message": "Success!",
                "access_token": new_access_token,
                "refresh_token": str(new_refresh_token)
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except TokenError:
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
