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
    'TransferredCarListOutputSerializer',
    'TransferredCarListItemSerializer',
    'TransferredCarAdditionService',
    'TransferredCarListInputSerializer',
)


class TransferredCarAdditionService(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    count = serializers.IntegerField()


class TransferredCarListItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    number = serializers.CharField()
    class_type = serializers.CharField()
    wash_type = serializers.CharField()
    car_wash_id = serializers.IntegerField()
    car_wash_name = serializers.CharField()
    windshield_washer_refilled_bottle_percentage = serializers.IntegerField()
    additional_services = serializers.ListField(
        child=TransferredCarAdditionService(),
    )
    created_at = serializers.DateTimeField()


class TransferredCarListOutputSerializer(serializers.Serializer):
    shift_id = serializers.IntegerField()
    shift_date = serializers.DateField()
    staff_id = serializers.IntegerField()
    staff_full_name = serializers.CharField()
    transferred_cars = serializers.ListField(
        child=TransferredCarListItemSerializer(),
    )


class TransferredCarListInputSerializer(serializers.Serializer):
    shift_id = serializers.IntegerField()


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
    windshield_washer_refilled_bottle_percentage = serializers.IntegerField()
    additional_services = AdditionalServiceSerializer(many=True, default=list)
