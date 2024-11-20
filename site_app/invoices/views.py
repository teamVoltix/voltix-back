from django.http import HttpResponse, FileResponse
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .serializers import InvoiceUploadSerializer
import logging
# este funcciona? hmmmmm///
logger = logging.getLogger(__name__)

# TEMP_FOLDER = settings.FILE_UPLOAD_TEMP_DIR or os.path.join(settings.BASE_DIR, 'temp_uploads')
# os.makedirs(TEMP_FOLDER, exist_ok=True)

def index(request):
    return HttpResponse("Invoices!")

class InvoiceUploadView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):

        logger.info("Received a file upload request.")
        serializer = InvoiceUploadSerializer(data=request.data)

        if serializer.is_valid():
            try:
                uploaded_file = serializer.validated_data['file']

                # Get TEMP_FOLDER from settings.py
                temp_folder = settings.FILE_UPLOAD_TEMP_DIR

                # Save file in chunks for memory efficiency
                file_path = os.path.join(temp_folder, uploaded_file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                logger.info(f"File '{uploaded_file.name}' uploaded successfully to {file_path}.")

                return Response({
                    'status': 'success',
                    'message': 'File uploaded successfully!',
                    'file_name': uploaded_file.name,
                    'file_path': file_path
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Error while saving file: {str(e)}")
                return Response({
                    'status': 'error',
                    'message': 'An error occurred while uploading the file.',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.warning("File upload validation failed: %s", serializer.errors)
        return Response({'status': 'error', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, *args, **kwargs):
    #     """
    #     Cleanup method to delete temporary files after processing.
    #     """
    #     file_name = request.data.get('file_name')
    #     if not file_name:
    #         logger.warning("File name not provided for deletion.")
    #         return Response({'status': 'error', 'message': 'File name not provided.'}, status=status.HTTP_400_BAD_REQUEST)

    #     file_path = os.path.join(TEMP_FOLDER, file_name)
    #     if os.path.exists(file_path):
    #         try:
    #             os.remove(file_path)
    #             logger.info(f"File '{file_name}' deleted successfully.")
    #             return Response({'status': 'success', 'message': 'File deleted successfully.'}, status=status.HTTP_200_OK)
    #         except Exception as e:
    #             logger.error(f"Error while deleting file '{file_name}': {str(e)}")
    #             return Response({
    #                 'status': 'error',
    #                 'message': 'An error occurred while deleting the file.',
    #                 'details': str(e)
    #             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     else:
    #         logger.warning(f"File '{file_name}' not found for deletion.")
    #         return Response({'status': 'error', 'message': 'File not found.'}, status=status.HTTP_404_NOT_FOUND)
