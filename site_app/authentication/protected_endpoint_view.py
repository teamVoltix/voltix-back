from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProtectedEndpointView(APIView):
    """
    A simple protected endpoint to test authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Access granted to the protected endpoint."})
