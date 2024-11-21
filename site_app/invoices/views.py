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

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import os
import uuid
import cv2

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import uuid
import cv2
import logging

logger = logging.getLogger(__name__)

class InvoiceUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="Subir y procesar facturas en PDF",
        operation_description=(
            "Permite a un usuario autenticado subir un archivo PDF. "
            "El archivo se convierte en imágenes, se procesa usando OpenCV y se guarda temporalmente."
        ),
        manual_parameters=[ 
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="El archivo PDF a subir y procesar.",
            ),
        ],
        responses={
            201: openapi.Response(
                description="File uploaded and processed successfully.",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "File uploaded successfully!",
                        "processed_images_count": 5,
                    }
                },
            ),
            400: openapi.Response(
                description="Validation error in the uploaded file.",
                examples={
                    "application/json": {
                        "status": "error",
                        "details": {
                            "file": [
                                "This field is required.",
                                "File size exceeds 5 MB.",
                                "Invalid file type: application/msword. Only PDF files are allowed.",
                                "File extension does not match content type. Only '.pdf' files are allowed.",
                                "File name must end with '.pdf'."
                            ],
                        }
                    }
                },
            ),
            500: openapi.Response(
                description="Server error during file upload or processing.",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "An error occurred while uploading the file.",
                        "details": "File processing failed due to XYZ error.",
                    }
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        logger.info("Received a file upload request.")
        serializer = InvoiceUploadSerializer(data=request.data)

        if serializer.is_valid():
            try:
                uploaded_file = serializer.validated_data['file']

                temp_folder = settings.FILE_UPLOAD_TEMP_DIR

                file_path = os.path.join(temp_folder, uploaded_file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                logger.info(f"File '{uploaded_file.name}' uploaded successfully to {file_path}.")

                images = pdf_to_images(file_path)
                processed_images = []

                for idx, img_data in enumerate(images):
                    grayscale_image = process_image(img_data)
                    processed_images.append(grayscale_image)

                    file_name_without_extension = os.path.splitext(uploaded_file.name)[0]
                    unique_id = uuid.uuid4().hex
                    output_path = os.path.join(
                        temp_folder, f"{file_name_without_extension}_page_{idx + 1}_{unique_id}.png"
                    )
                    cv2.imwrite(output_path, grayscale_image)
                    logger.info(f"Processed image saved in: {output_path}")

                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"PDF file '{uploaded_file.name}' deleted.")

                logger.info("PDF successfully converted to images and processed using OpenCV.")

                return Response(
                    {
                        "status": "success",
                        "message": "File uploaded successfully!",
                        "processed_images_count": len(processed_images),
                    },
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                logger.error(f"Error while saving file: {str(e)}")
                return Response(
                    {
                        "status": "error",
                        "message": "An error occurred while uploading the file.",
                        "details": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        logger.warning("File upload validation failed: %s", serializer.errors)
        return Response(
            {"status": "error", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

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

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import InvoiceSerializer
from datetime import datetime
import random

class InvoiceSearchView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Search Invoices",
        operation_description="Retrieves a list of invoices for the authenticated user. This is based on a dummy dataset.",
        responses={
            200: openapi.Response(
                description="List of invoices retrieved successfully.",
                examples={
                    "application/json": [
                        {
                            "invoice_id": 1,
                            "user_id": 1,
                            "upload_date": "2024-11-21T12:00:00.000Z",
                            "amount_due": 250.75,
                            "due_date": "2024-12-01T12:00:00.000Z",
                            "provider": "Proveedor A",
                            "file_path": "/fake/path/invoice1.pdf",
                            "ocr_data": {"field": "value1"},
                        },
                        {
                            "invoice_id": 2,
                            "user_id": 1,
                            "upload_date": "2024-11-22T12:00:00.000Z",
                            "amount_due": 500.30,
                            "due_date": "2024-12-15T12:00:00.000Z",
                            "provider": "Proveedor B",
                            "file_path": "/fake/path/invoice2.pdf",
                            "ocr_data": {"field": "value2"},
                        },
                    ]
                },
            ),
            401: openapi.Response(
                description="Unauthorized. User not authenticated.",
                examples={
                    "application/json": {
                        "detail": "Authentication credentials were not provided."
                    }
                },
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        fake_invoices = [
            {
                "invoice_id": 1,
                "user_id": request.user.id,
                "upload_date": datetime.now().isoformat(),
                "amount_due": round(random.uniform(100, 1000), 2),
                "due_date": datetime.now().isoformat(),
                "provider": "Proveedor A",
                "file_path": "/fake/path/invoice1.pdf",
                "ocr_data": {"field": "value1"},
            },
            {
                "invoice_id": 2,
                "user_id": request.user.id,
                "upload_date": datetime.now().isoformat(),
                "amount_due": round(random.uniform(100, 1000), 2),
                "due_date": datetime.now().isoformat(),
                "provider": "Proveedor B",
                "file_path": "/fake/path/invoice2.pdf",
                "ocr_data": {"field": "value2"},
            },
        ]

        user_invoices = [invoice for invoice in fake_invoices if invoice["user_id"] == request.user.id]

        serializer = InvoiceSerializer(user_invoices, many=True)
        return Response(serializer.data)
