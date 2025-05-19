from rest_framework import serializers


class CarWashServicePriceUpsertInputSerializer(serializers.Serializer):
    price = serializers.IntegerField(min_value=0, max_value=1_000_000)


class CarWashServicePriceUpsertOutputSerializer(serializers.Serializer):
    car_wash_id = serializers.IntegerField()
    service_id = serializers.UUIDField()
    price = serializers.IntegerField()
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
