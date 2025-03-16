from rest_framework import serializers

from shifts.models import CarToWash, CarToWashAdditionalService
from shifts.serializers.additional_services import AdditionalServiceSerializer


__all__ = (
    "TransferredCarCreateInputSerializer",
    "TransferredCarCreateOutputSerializer",
    "TransferredCarUpdateInputSerializer",
    "CarToWashAdditionalServiceSerializer",
    "TransferredCarListOutputSerializer",
    "TransferredCarListItemSerializer",
    "TransferredCarAdditionService",
    "TransferredCarListInputSerializer",
    "TransferredCarDetailOutputSerializer",
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
    windshield_washer_type = serializers.ChoiceField(
        choices=CarToWash.WindshieldWasherType.choices,
    )
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


class TransferredCarDetailOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    shift_id = serializers.IntegerField()
    shift_date = serializers.DateField()
    staff_id = serializers.IntegerField()
    staff_full_name = serializers.CharField()
    number = serializers.CharField()
    class_type = serializers.CharField()
    wash_type = serializers.CharField()
    car_wash_id = serializers.IntegerField()
    car_wash_name = serializers.CharField()
    windshield_washer_type = serializers.ChoiceField(
        choices=CarToWash.WindshieldWasherType.choices,
    )
    windshield_washer_refilled_bottle_percentage = serializers.IntegerField()
    additional_services = serializers.ListField(
        child=TransferredCarAdditionService(),
    )
    created_at = serializers.DateTimeField()


class TransferredCarCreateInputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    number = serializers.CharField()
    car_class = serializers.ChoiceField(choices=CarToWash.CarType.choices)
    wash_type = serializers.ChoiceField(choices=CarToWash.WashType.choices)
    windshield_washer_type = serializers.ChoiceField(
        choices=CarToWash.WindshieldWasherType.choices,
    )
    windshield_washer_refilled_bottle_percentage = serializers.IntegerField()
    additional_services = AdditionalServiceSerializer(many=True, default=list)


class TransferredCarCreateOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    shift_id = serializers.IntegerField()
    number = serializers.CharField()
    class_type = serializers.CharField()
    wash_type = serializers.CharField()
    windshield_washer_refilled_bottle_percentage = serializers.IntegerField()
    car_wash_id = serializers.IntegerField()
    additional_services = AdditionalServiceSerializer(many=True)


class CarToWashAdditionalServiceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="service_id")

    class Meta:
        model = CarToWashAdditionalService
        fields = ("id", "count")


class TransferredCarUpdateInputSerializer(serializers.Serializer):
    number = serializers.CharField(allow_null=True, default=None)
    car_wash_id = serializers.CharField(allow_null=True, default=None)
    class_type = serializers.ChoiceField(
        choices=CarToWash.CarType.choices,
        allow_null=True,
        default=None,
    )
    wash_type = serializers.ChoiceField(
        choices=CarToWash.WashType.choices,
        allow_null=True,
        default=None,
    )
    windshield_washer_type = serializers.ChoiceField(
        choices=CarToWash.WindshieldWasherType.choices,
    )
    windshield_washer_refilled_bottle_percentage = serializers.CharField(
        allow_null=True,
        default=None,
    )
    additional_services = serializers.ListSerializer(
        child=AdditionalServiceSerializer(),
        allow_null=True,
        default=None,
    )
