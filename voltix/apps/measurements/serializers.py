from rest_framework import serializers
from apps.voltix.models import Measurement

class MeasurementSerializer(serializers.ModelSerializer):
    comparison_status = serializers.CharField(read_only=True)

    class Meta:
        model = Measurement
        fields = '__all__'