from rest_framework import serializers


class CarWashRetrieveServiceParentSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class CarWashRetrieveServiceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    is_countable = serializers.BooleanField()
    price = serializers.IntegerField()
    parent = CarWashRetrieveServiceParentSerializer(allow_null=None)
    max_count = serializers.IntegerField()
    is_dry_cleaning = serializers.BooleanField()


class CarWashRetrieveOutputSerializer(serializers.Serializer):
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
    services = CarWashRetrieveServiceSerializer(many=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
