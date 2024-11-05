from rest_framework import serializers
from shifts.models import CarToWash

__all__ = (
    'AdditionalServiceSerializer',
    'CarToWashCreateInputSerializer',
)


class AdditionalServiceSerializer(serializers.Serializer):
    name = serializers.CharField()
    count = serializers.IntegerField()


class CarToWashCreateInputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    number = serializers.CharField()
    car_class = serializers.ChoiceField(choices=CarToWash.CarType.choices)
    wash_type = serializers.ChoiceField(choices=CarToWash.WashType.choices)
    windshield_washer_refilled_bottle_percentage = (
        serializers.IntegerField()
    )
    additional_services = AdditionalServiceSerializer(
        many=True,
        default=list,
    )
