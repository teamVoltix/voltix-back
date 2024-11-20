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
# Librerías para IMG
import fitz  
import cv2
import numpy as np
import uuid
# este funcciona? hmmmmm///
logger = logging.getLogger(__name__)

# TEMP_FOLDER = settings.FILE_UPLOAD_TEMP_DIR or os.path.join(settings.BASE_DIR, 'temp_uploads')
# os.makedirs(TEMP_FOLDER, exist_ok=True)

def index(request):
    return HttpResponse("Invoices!")

def pdf_to_images(pdf_path):
    """
    Converts a PDF file into images (one image per page).
    """
    images = []
    try:
        pdf_document = fitz.open(pdf_path)
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            pix = page.get_pixmap()
            image_data = pix.tobytes("png")
            images.append(image_data)
        pdf_document.close()
        return images
    except Exception as e:
        logger.error(f"Error al convertir PDF a imágenes: {str(e)}")
        return []
    
def process_image(image_data):
    """
    Converts an image to grayscale using OpenCV.
    """
    np_array = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return grayscale_image

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

                 # Convert PDF to images
                images = pdf_to_images(file_path)
                processed_images = []

                #we apply OpenCV here
                for idx, img_data in enumerate(images):
                    grayscale_image = process_image(img_data)
                    processed_images.append(grayscale_image)
                        
                        # Save the image to the temporary folder
                    file_name_without_extension = os.path.splitext(uploaded_file.name)[0]  #Name without extension
                    unique_id = uuid.uuid4().hex
                    output_path = os.path.join(temp_folder, f"{file_name_without_extension}_page_{idx + 1}_{unique_id}.png")   
                    cv2.imwrite(output_path, grayscale_image)
                    logger.info(f"Processed image saved in: {output_path}")
                 
                 # After processing the PDF, delete the PDF file if it's no longer needed
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"PDF file '{uploaded_file.name}' deleted.")


                logger.info("PDF successfully converted to images and processed using OpenCV.")


                return Response({
                    'status': 'success',
                    'message': 'File uploaded successfully!',
                    #'file_name': uploaded_file.name,
                    #'file_path': file_path,
                    'processed_images_count': len(processed_images)
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
