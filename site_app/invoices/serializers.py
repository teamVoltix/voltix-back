import mimetypes
from rest_framework import serializers

class InvoiceUploadSerializer(serializers.Serializer):
    """
    Serializer to handle file upload validations.
    """
    file = serializers.FileField()

    def validate_file(self, value):
        """
        Validate the uploaded file for size, type, and extension.
        """
        # File size limit: 5 MB
        max_size = 5 * 1024 * 1024  # 5 MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError("File size exceeds 5 MB.")

        # Allowed file types
        allowed_types = ['application/pdf', 'image/png', 'image/jpeg']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"Invalid file type: {value.content_type}. Allowed types are PDF, PNG, and JPEG."
            )

        # Verify file extension matches content type
        ext = mimetypes.guess_extension(value.content_type)
        if ext and not value.name.endswith(ext):
            raise serializers.ValidationError(
                f"File extension does not match content type: Expected {ext}"
            )

        return value

