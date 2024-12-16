# from rest_framework import serializers
from apps.general.models import Measurement

# class MeasurementSerializer(serializers.ModelSerializer):
#     comparison_status = serializers.CharField(read_only=True)

#     class Meta:
#         model = Measurement
#         fields = '__all__'


from rest_framework import serializers

class MeasurementSerializer(serializers.ModelSerializer):
    comparison_status = serializers.CharField(read_only=True)
    measurement_start = serializers.SerializerMethodField()
    measurement_end = serializers.SerializerMethodField()

    class Meta:
        model = Measurement
        fields = ['id', 'user', 'measurement_start', 'measurement_end', 'data', 'created_at', 'updated_at', 'comparison_status']

    def get_measurement_start(self, obj):
        return obj.measurement_start.strftime('%Y-%m-%d') if obj.measurement_start else None

    def get_measurement_end(self, obj):
        return obj.measurement_end.strftime('%Y-%m-%d') if obj.measurement_end else None
