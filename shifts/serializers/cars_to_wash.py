from rest_framework import serializers

from shifts.models import CarToWash, CarToWashAdditionalService
from shifts.serializers.additional_services import AdditionalServiceSerializer
from shifts.serializers.car_washes import CarWashSerializer

__all__ = (
    'CarToWashCreateInputSerializer',
    'CarToWashCreateOutputSerializer',
    'CarToWashDetailOutputSerializer',
    'UpdateCarToWashInputSerializer',
    'CarToWashAdditionalServiceSerializer',
)


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


class CarToWashAdditionalServiceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='service_id')

    class Meta:
        model = CarToWashAdditionalService
        fields = ('id', 'count')


class CarToWashDetailOutputSerializer(serializers.ModelSerializer):
    class_type = serializers.CharField(source='car_class')
    car_wash = CarWashSerializer(allow_null=True)
    additional_services = CarToWashAdditionalServiceSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = CarToWash
        fields = (
            'id',
            'number',
            'wash_type',
            'class_type',
            'windshield_washer_refilled_bottle_percentage',
            'created_at',
            'additional_services',
            'car_wash',
        )


class UpdateCarToWashInputSerializer(serializers.Serializer):
    additional_services = AdditionalServiceSerializer(many=True, default=list)
