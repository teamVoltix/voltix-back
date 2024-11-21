from django.http import JsonResponse
from PIL import Image
import pytesseract

def process_invoice(request):
    # Ruta a la imagen que quieres procesar
    image_path = '/workspaces/i004-voltix-back/site_app/media/temp/endesa4_page_1_a780fe3eb2c24beabbe6bd20d1bdd336.png'

    try:
        # Cargar la imagen
        image = Image.open(image_path)
        custom_oem_psm_config = r'--oem 3 --psm 11'
        

        # Asegúrate de que Tesseract esté en la ubicación correcta
        pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"  # Cambia esta ruta si Tesseract está en otra ubicación

        # Realiza la extracción de texto
        text = pytesseract.image_to_string(image, lang='spa', config=custom_oem_psm_config)  # Asegúrate de tener el idioma 'spa' instalado

        # Retorna el texto extraído como respuesta JSON
        return JsonResponse({"text": text})

    except Exception as e:
        # Manejo de error si hay un problema con la imagen o Tesseract
        return JsonResponse({"error": f"Error al procesar la imagen: {str(e)}"}, status=500)
