from rest_framework import serializers

from car_washes.models import CarWash


class CarWashServiceListInputSerializer(serializers.Serializer):
    car_wash_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        default=None,
    )


class CarWashServiceParentSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class CarWashServiceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    is_countable = serializers.BooleanField()
    parent = CarWashServiceParentSerializer()
    max_count = serializers.IntegerField()


class CarWashListInputSerializer(serializers.Serializer):
    include_hidden = serializers.BooleanField(default=True)


class CarWashListOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    car_transporters_comfort_class_car_washing_price = (
        serializers.IntegerField(source="comfort_class_car_washing_price")
    )
    car_transporters_business_class_car_washing_price = (
        serializers.IntegerField(source="business_class_car_washing_price")
    )
    car_transporters_van_washing_price = serializers.IntegerField(
        source="van_washing_price",
    )
    car_transporters_and_washers_comfort_class_price = (
        serializers.IntegerField()
    )
    car_transporters_and_washers_business_class_price = (
        serializers.IntegerField()
    )
    car_transporters_and_washers_van_price = serializers.IntegerField()
    windshield_washer_price_per_bottle = serializers.IntegerField()
    is_hidden = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

class CarWashRetrieveOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarWash
        fields = (
            "id",
            "name",
            "comfort_class_car_washing_price",
            "business_class_car_washing_price",
            "van_washing_price",
            "windshield_washer_price_per_bottle",
            "is_hidden",
            "created_at",
            "updated_at",
        )


class CarWashUpdateInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    comfort_class_car_washing_price = serializers.IntegerField(min_value=0)
    business_class_car_washing_price = serializers.IntegerField(min_value=0)
    van_washing_price = serializers.IntegerField(min_value=0)
    windshield_washer_price_per_bottle = serializers.IntegerField(min_value=0)
    is_hidden = serializers.BooleanField()


class CarWashUpdateOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    comfort_class_car_washing_price = serializers.IntegerField()
    business_class_car_washing_price = serializers.IntegerField()
    van_washing_price = serializers.IntegerField()
    windshield_washer_price_per_bottle = serializers.IntegerField()
    is_hidden = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class CarWashCreateInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    car_transporters_comfort_class_car_washing_price = (
        serializers.IntegerField(default=0)
    )
    car_transporters_business_class_car_washing_price = (
        serializers.IntegerField(default=0)
    )
    car_transporters_van_washing_price = serializers.IntegerField()
    car_transporters_and_washers_comfort_class_price = (
        serializers.IntegerField(default=0)
    )
    car_transporters_and_washers_business_class_price = (
        serializers.IntegerField(default=0)
    )
    car_transporters_and_washers_van_price = (
        serializers.IntegerField(default=0)
    )
    windshield_washer_price_per_bottle = serializers.IntegerField(default=0)
    is_hidden = serializers.BooleanField(default=False)


class CarWashCreateOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    car_transporters_comfort_class_car_washing_price = (
        serializers.IntegerField()
    )
    car_transporters_business_class_car_washing_price = (
        serializers.IntegerField()
    )
    car_transporters_van_washing_price = serializers.IntegerField()
    car_transporters_and_washers_comfort_class_price = (
        serializers.IntegerField()
    )
    car_transporters_and_washers_business_class_price = (
        serializers.IntegerField()
    )
    car_transporters_and_washers_van_price = serializers.IntegerField()
    windshield_washer_price_per_bottle = serializers.IntegerField()
    is_hidden = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class CarWashServicePriceUpsertInputSerializer(serializers.Serializer):
    price = serializers.IntegerField(min_value=0, max_value=1_000_000)


class CarWashServicePriceUpsertOutputSerializer(serializers.Serializer):
    car_wash_id = serializers.IntegerField()
    service_id = serializers.UUIDField()
    price = serializers.IntegerField()
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()


class CarWashServicePriceListItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    price = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class CarWashServicePriceListOutputSerializer(serializers.Serializer):
    car_wash_id = serializers.IntegerField()
    car_wash_name = serializers.CharField()
    planned_car_transfer_price = serializers.IntegerField()
    business_car_transfer_price = serializers.IntegerField()
    van_transfer_price = serializers.IntegerField()
    windshield_washer_bottle_price = serializers.IntegerField()
    services = CarWashServicePriceListItemSerializer(many=True)
