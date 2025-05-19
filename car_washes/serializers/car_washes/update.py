from rest_framework import serializers


class CarWashUpdateInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
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
    car_transporters_and_washers_van_price = (
        serializers.IntegerField()
    )
    windshield_washer_price_per_bottle = serializers.IntegerField()
    is_hidden = serializers.BooleanField()


class CarWashUpdateOutputSerializer(serializers.Serializer):
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
