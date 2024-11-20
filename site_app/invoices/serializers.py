import mimetypes
from rest_framework import serializers

class InvoiceUploadSerializer(serializers.Serializer):

    file = serializers.FileField()

    def validate_file(self, value):

        max_size = 5 * 1024 * 1024  #5mb
        if value.size > max_size:
            raise serializers.ValidationError("File size exceeds 5 MB.")

        allowed_types = ['application/pdf', 'image/png', 'image/jpeg']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"Invalid file type: {value.content_type}. Allowed types are PDF, PNG, and JPEG."
            )
        
        ext = mimetypes.guess_extension(value.content_type)
        if ext and not value.name.endswith(ext):
            raise serializers.ValidationError(
                f"File extension does not match content type: Expected {ext}"
            )

        return value

"""
# ONLY PDF VERSION
import mimetypes
from rest_framework import serializers

class InvoiceUploadSerializer(serializers.Serializer):

    file = serializers.FileField()

    def validate_file(self, value):

        max_size = 5 * 1024 * 1024  # 5 MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError("File size exceeds 5 MB.")

        if value.content_type != 'application/pdf':
            raise serializers.ValidationError(
                f"Invalid file type: {value.content_type}. Only PDF files are allowed."
            )

        ext = mimetypes.guess_extension(value.content_type)
        if not ext or ext != '.pdf':
            raise serializers.ValidationError(
                "File extension does not match content type. Only '.pdf' files are allowed."
            )

        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("File name must end with '.pdf'.")

        return value

"""