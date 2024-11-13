from rest_framework import serializers

from shifts.models import AvailableDate, CarToWash, Shift

__all__ = (
    'AdditionalServiceSerializer',
    'CarToWashCreateInputSerializer',
    'CarToWashCreateOutputSerializer',
    'AvailableDateSerializer',
    'DateSerializer',
    'ShiftListForSpecificDateOutputSerializer',
)


class DateSerializer(serializers.Serializer):
    date = serializers.DateField()


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


class AvailableDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableDate
        fields = ('id', 'month', 'year')


class ShiftListForSpecificDateOutputSerializer(
    serializers.ModelSerializer,
):
    class Meta:
        model = Shift
        fields = (
            'id',
            'date',
            'staff',
            'is_started',
            'is_finished',
            'created_at',
        )
        depth = 1
