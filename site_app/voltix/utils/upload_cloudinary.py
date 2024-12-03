from cloudinary.uploader import upload
from cloudinary.exceptions import Error as CloudinaryError
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def process_and_upload_image(photo, folder="profiles", max_size=5 * 1024 * 1024):
    """
    Valida, procesa y sube una imagen a Cloudinary.

    Args:
        photo (InMemoryUploadedFile): El archivo de imagen cargado.
        folder (str): Carpeta en Cloudinary donde se almacenará la imagen.
        max_size (int): Tamaño máximo permitido para la imagen en bytes.

    Returns:
        str: URL de la imagen subida a Cloudinary.

    Raises:
        ValueError: Si la imagen no cumple con las validaciones.
        CloudinaryError: Si hay un error al subir la imagen.
    """
    # Validar tipo de archivo
    if photo.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
        raise ValueError("Tipo de archivo no válido.")

    # Validar tamaño del archivo
    max_size_mb = max_size / (1024 * 1024)  # Convertir a MB
    if photo.size > max_size:
        raise ValueError(f"El archivo excede el tamaño máximo permitido de {max_size_mb:.2f} MB.")

    try:
        # Reprocesar la imagen para eliminar metadatos problemáticos
        img = Image.open(photo)
        img_format = img.format  # Mantener el formato original (JPEG, PNG, etc.)
        img_output = BytesIO()
        img.save(img_output, format=img_format)  # Guardar en un buffer para eliminar metadatos
        img_output.seek(0)  # Mover el puntero al inicio del buffer

        # Convertir la imagen procesada a un archivo compatible con Django
        processed_photo = InMemoryUploadedFile(
            img_output,
            'ImageField',
            photo.name,
            photo.content_type,
            img_output.tell(),
            None
        )

        # Subir la imagen procesada a Cloudinary
        upload_result = upload(processed_photo, folder=folder, overwrite=True, resource_type="image")
        photo_url = upload_result.get("secure_url")
        if not photo_url:
            raise CloudinaryError("Error al subir la imagen a Cloudinary.")

        return photo_url

    except IOError:
        raise ValueError("El archivo está corrupto o no es una imagen válida.")
