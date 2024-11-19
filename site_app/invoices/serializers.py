from rest_framework import serializers

class InvoiceUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):

        max_size = 5 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("File size exceeds 5 MB.")

        allowed_types = ['application/pdf', 'image/png', 'image/jpeg']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"Invalid file type: {value.content_type}. Allowed types are PDF, PNG, and JPEG."
            )
        return value
