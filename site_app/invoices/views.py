import os
import uuid
import cv2
import pytesseract
import logging
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import InvoiceUploadSerializer
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class InvoiceProcessView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="Subir y procesar facturas en PDF (OCR incluido)",
        operation_description=(
            "Permite a un usuario autenticado subir un archivo PDF, "
            "convertirlo en imágenes, procesarlas (escalado a grises) y ejecutar OCR para extraer texto."
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
                description="Archivo procesado y texto extraído exitosamente.",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Archivo procesado y texto extraído exitosamente.",
                        "extracted_text": "Texto extraído del archivo...",
                    }
                },
            ),
            400: openapi.Response(
                description="Error en la validación del archivo.",
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
                description="Error durante el procesamiento.",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Error durante el procesamiento.",
                        "details": "Detalles del error...",
                    }
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = InvoiceUploadSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uploaded_file = serializer.validated_data["file"]

                # Crear carpeta temporal si no existe
                temp_folder = settings.FILE_UPLOAD_TEMP_DIR or os.path.join(settings.BASE_DIR, "media", "temp")
                os.makedirs(temp_folder, exist_ok=True)

                # Guardar archivo temporalmente
                file_path = os.path.join(temp_folder, uploaded_file.name)
                with open(file_path, "wb+") as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                logger.info(f"Archivo '{uploaded_file.name}' subido exitosamente a {file_path}.")

                # Convertir PDF a imágenes
                images = self.pdf_to_images(file_path)
                processed_images = []

                # Procesar imágenes y guardar escala de grises
                for idx, img_data in enumerate(images):
                    grayscale_image = self.process_image(img_data)
                    processed_images.append(grayscale_image)

                    file_name_without_extension = os.path.splitext(uploaded_file.name)[0]
                    unique_id = uuid.uuid4().hex
                    output_path = os.path.join(
                        temp_folder, f"{file_name_without_extension}_page_{idx + 1}_{unique_id}.png"
                    )
                    cv2.imwrite(output_path, grayscale_image)
                    logger.info(f"Imagen procesada guardada en: {output_path}")

                # Realizar OCR en la primera imagen
                if processed_images:
                    ocr_text = self.perform_ocr(processed_images[0])
                    parsed_data = self.convert_ocr_to_json(ocr_text)
                else:
                    ocr_text = "No se pudieron procesar las imágenes para OCR."
                    parsed_data = {}

                # Eliminar el archivo PDF subido
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Archivo PDF '{uploaded_file.name}' eliminado.")

                return Response(
                    {
                        "status": "success",
                        "message": "Archivo procesado y texto extraído exitosamente.",
                        "extracted_text": ocr_text,
                        "parsed_data": parsed_data,
                        "processed_images_count": len(processed_images),
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                logger.error(f"Error durante el procesamiento: {str(e)}")
                return Response(
                    {
                        "status": "error",
                        "message": "Error durante el procesamiento.",
                        "details": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        logger.warning(f"Validación fallida: {serializer.errors}")
        return Response({"status": "error", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def pdf_to_images(self, pdf_path):
        """
        Convierte un archivo PDF en imágenes (una por página).
        """
        images = []
        try:
            pdf_document = fitz.open(pdf_path)
            for page_number in range(len(pdf_document)):
                page = pdf_document[page_number]
                # pix = page.get_pixmap()
                ##########################################################
                zoom_x, zoom_y = 2.0, 2.0  # 2x scaling for higher DPI
                matrix = fitz.Matrix(zoom_x, zoom_y)
                pix = page.get_pixmap(matrix=matrix)
                #########################################################
                image_data = pix.tobytes("png")
                images.append(image_data)
            pdf_document.close()
            return images
        except Exception as e:
            logger.error(f"Error al convertir PDF a imágenes: {str(e)}")
            return []

    def process_image(self, image_data):
        """
        Convierte una imagen a escala de grises usando OpenCV.
        """
        try:
            np_array = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # return grayscale_image
        #####################################################################
        # Increase contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            contrast_image = clahe.apply(grayscale_image)

            # Remove noise
            denoised_image = cv2.fastNlMeansDenoising(contrast_image, None, 30, 7, 21)


        # Sharpen the image
            kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
            sharpened_image = cv2.filter2D(denoised_image, -1, kernel)

            return sharpened_image
        except Exception as e:
            logger.error(f"Error during image preprocessing: {str(e)}")
            return None
##################################################################
    def perform_ocr(self, image):
        """
        Realiza OCR en una imagen usando Tesseract y retorna el texto extraído.
        """
        try:
            custom_oem_psm_config = r"--oem 3 --psm 11"
            pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"  # Ajustar según tu entorno

            # Convertir imagen OpenCV a imagen PIL
            pil_image = Image.fromarray(image)

            # Realiza la extracción de texto
            ocr_result = pytesseract.image_to_string(pil_image, lang="spa", config=custom_oem_psm_config)
        
            return ocr_result

        except Exception as e:
            logger.error(f"Error al realizar OCR: {str(e)}")
            return {"error": f"Error al procesar la imagen: {str(e)}"}

    def convert_ocr_to_json(self, ocr_text):
        """
        Convierte el texto OCR extraído a un JSON con el esquema proporcionado.
        """
        try:
            import re
            from datetime import datetime

            # Función para formatear la fecha
            def format_date(date_str):
                try:
                    return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                except ValueError:
                    return None

            # Extraer datos del texto usando expresiones regulares
            nombre_cliente = re.search(r"Nombre del cliente:\s*(.+)", ocr_text)
            numero_referencia = re.search(r"Referencia:\s*(.+)", ocr_text)
            fecha_emision = re.search(r"Fecha emisión factura:\s*(\d{2}/\d{2}/\d{4})", ocr_text)
            periodo_inicio = re.search(r"Periodo de facturación: del\s*(\d{2}/\d{2}/\d{4})", ocr_text)
            periodo_fin = re.search(r"a\s*(\d{2}/\d{2}/\d{4})", ocr_text)  # Ajuste para capturar "a dd/mm/yyyy"
            dias = re.search(r"\((\d+)\s*días\)", ocr_text)
            forma_pago = re.search(r"Forma de pago:\s*(.+)", ocr_text)
            fecha_cargo = re.search(r"Fecha de cargo:\s*(\d{2}/\d{2}/\d{4})", ocr_text)
            mandato = re.search(r"Cod\.Mandato:\s*(.+)", ocr_text)

            # Extraer datos financieros
            costo_potencia = re.search(r"Potencia\s+([\d,\.]+)", ocr_text)
            costo_energia = re.search(r"Energía\s+([\d,\.]+)", ocr_text)
            descuentos = re.search(r"Descuentos\s+([\d,\.]+)", ocr_text)
            impuestos = re.search(r"Impuestos\s+([\d,\.]+)", ocr_text)
            total_a_pagar = re.search(r"Total\s+([\d,\.]+)", ocr_text)

            # Detalles de consumo
            consumo_punta = re.search(r"Consumo punta\s+([\d,\.]+)", ocr_text)
            consumo_valle = re.search(r"Consumo valle\s+([\d,\.]+)", ocr_text)
            consumo_total = re.search(r"Consumo total\s+([\d,\.]+)", ocr_text)
            precio_efectivo_energia = re.search(r"ha salido a\s*([\d,\.]+)\s*€/kWh", ocr_text)

            # Construir JSON
            parsed_data = {
                "nombre_cliente": nombre_cliente.group(1) if nombre_cliente else None,
                "numero_referencia": numero_referencia.group(1) if numero_referencia else None,
                "fecha_emision": format_date(fecha_emision.group(1)) if fecha_emision else None,
                "periodo_facturacion": {
                    "inicio": format_date(periodo_inicio.group(1)) if periodo_inicio else None,
                    "fin": format_date(periodo_fin.group(1)) if periodo_fin else None,  # Capturamos y formateamos fecha de fin
                    "dias": int(dias.group(1)) if dias else None,
                },
                "forma_pago": forma_pago.group(1) if forma_pago else None,
                "fecha_cargo": format_date(fecha_cargo.group(1)) if fecha_cargo else None,
                "mandato": mandato.group(1) if mandato else None,
                "desglose_cargos": {
                    "costo_potencia": float(costo_potencia.group(1).replace(",", ".")) if costo_potencia else None,
                    "costo_energia": float(costo_energia.group(1).replace(",", ".")) if costo_energia else None,
                    "descuentos": float(descuentos.group(1).replace(",", ".")) if descuentos else None,
                    "impuestos": float(impuestos.group(1).replace(",", ".")) if impuestos else None,
                    "total_a_pagar": float(total_a_pagar.group(1).replace(",", ".")) if total_a_pagar else None,
                },
                "detalles_consumo": {
                    "consumo_punta": float(consumo_punta.group(1).replace(",", ".")) if consumo_punta else None,
                    "consumo_valle": float(consumo_valle.group(1).replace(",", ".")) if consumo_valle else None,
                    "consumo_total": float(consumo_total.group(1).replace(",", ".")) if consumo_total else None,
                    "precio_efectivo_energia": float(precio_efectivo_energia.group(1).replace(",", ".")) if precio_efectivo_energia else None,
                },
            }

            return parsed_data

        except Exception as e:
            logger.error(f"Error al convertir OCR a JSON: {str(e)}")
            return {"error": "Error al convertir OCR a JSON."}















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



################################################################################################################################
############################################ GET - VISUALIZAR FATURA POR ID ####################################################
################################################################################################################################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from voltix.models import Invoice  # Importar el modelo Invoice
from .serializers import InvoiceSerializer  # Usar el serializer existente

class InvoiceDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Asegurar que solo usuarios autenticados puedan acceder

    def get(self, request, invoice_id):
        # Obtener la factura por ID
        invoice = get_object_or_404(Invoice, pk=invoice_id)

        # Serializar la factura utilizando tu serializer existente
        serializer = InvoiceSerializer(invoice)

        # Retornar la respuesta JSON
        return Response(serializer.data, status=status.HTTP_200_OK)

################################################################################################################################