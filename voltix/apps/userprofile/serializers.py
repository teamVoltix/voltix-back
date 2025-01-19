from rest_framework import serializers
from apps.general.models import Profile, UploadLog
from django.core.exceptions import ValidationError
import hashlib

#utility fn
def calculate_file_hash(file):
    sha256 = hashlib.sha256()
    for chunk in file.chunks():
        sha256.update(chunk)
    return sha256.hexdigest()


# single reponsibility principle


class SingleFileValidatorSerializer(serializers.Serializer):
    def validate(self, attrs):
        if len(self.initial_data) != 1:
            raise serializers.ValidationError("You must upload exactly one file.")
        return attrs


class FileSizeValidatorSerializer(serializers.Serializer):
    photo = serializers.ImageField()

    def validate_photo(self, value):
        max_size = 5 * 1024 * 1024  # 5 MB
        if value.size > max_size:
            raise serializers.ValidationError("Image size cannot exceed 5 MB.")
        return value

class FileTypeValidatorSerializer(serializers.Serializer):
    photo = serializers.ImageField()

    def validate_photo(self, value):
        allowed_types = ['image/jpeg', 'image/png']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only JPEG and PNG images are allowed.")
        return value


class DuplicateFileValidatorSerializer(serializers.Serializer):
    photo = serializers.ImageField()

    def validate_photo(self, value):
        file_hash = calculate_file_hash(value)

        if UploadLog.objects.filter(file_hash=file_hash).exists():
            raise serializers.ValidationError("This image has already been uploaded.")
        value.seek(0)
        return value

class CombinedValidatorSerializer(serializers.Serializer):
    photo = serializers.ImageField()

    def validate(self, attrs):
        """
        Combine all individual validators to validate the photo field:
        1. File count validation (SingleFileValidatorSerializer).
        2. Duplicate file validation (DuplicateFileValidatorSerializer).
        3. File size validation (FileSizeValidatorSerializer).
        4. File type validation (FileTypeValidatorSerializer).
        """

        # Step 1: Validate the number of files
        file_count_validator = SingleFileValidatorSerializer(data=self.initial_data)
        file_count_validator.is_valid(raise_exception=True)

        # Extract the single file ???
        photo = next(iter(self.initial_data.values()))

        # Step 2: Validate duplicate file
        duplicate_validator = DuplicateFileValidatorSerializer(data={'photo': photo})
        duplicate_validator.is_valid(raise_exception=True)

        # Step 3: Validate file size
        size_validator = FileSizeValidatorSerializer(data={'photo': photo})
        size_validator.is_valid(raise_exception=True)

        # Step 4: Validate file type
        type_validator = FileTypeValidatorSerializer(data={'photo': photo})
        type_validator.is_valid(raise_exception=True)

        # Calculate file hash
        file_hash = calculate_file_hash(photo)

        # Reset file pointer after hash calculation
        photo.seek(0)

        # Add validated data to the serializer context
        attrs['photo'] = photo
        attrs['file_hash'] = file_hash
        return attrs
