from django.shortcuts import render
from django.http import HttpResponse
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .serializers import InvoiceUploadSerializer


TEMP_FOLDER = os.path.join(settings.BASE_DIR, 'temp_uploads')
os.makedirs(TEMP_FOLDER, exist_ok=True)


def index(request):
    return HttpResponse("Invoices!")

class InvoiceUploadView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = InvoiceUploadSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']

            fs = FileSystemStorage(location=TEMP_FOLDER)
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)

            return Response({
                'message': 'File uploaded successfully!',
                'file_name': filename,
                'file_path': file_path
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
