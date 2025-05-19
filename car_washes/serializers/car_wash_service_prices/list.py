from rest_framework import serializers


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
