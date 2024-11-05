from rest_framework import serializers
from shifts.models import CarToWash

__all__ = (
    'AdditionalServiceSerializer',
    'CarToWashCreateInputSerializer',
    'CarToWashCreateOutputSerializer',
)


class AdditionalServiceSerializer(serializers.Serializer):
    name = serializers.CharField()
    count = serializers.IntegerField()


class CarToWashCreateInputSerializer(serializers.ModelSerializer):
    staff_id = serializers.IntegerField()
    additional_services = AdditionalServiceSerializer(many=True, default=list)

    class Meta:
        model = CarToWash
        fields = (
            'staff_id',
            'number',
            'car_class',
            'wash_type',
            'windshield_washer_refilled_bottle_percentage',
            'additional_services',
        )


class CarToWashCreateOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    shift_id = serializers.IntegerField()
    number = serializers.CharField()
    class_type = serializers.CharField()
    wash_type = serializers.CharField()
    windshield_washer_refilled_bottle_percentage = serializers.IntegerField()
    car_wash_id = serializers.IntegerField()
    additional_services = AdditionalServiceSerializer(many=True)
