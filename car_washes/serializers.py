from rest_framework import serializers

from car_washes.models import CarWash

__all__ = (
    'CarWashListOutputSerializer',
    'CarWashRetrieveOutputSerializer',
    'CarWashCreateOutputSerializer',
    'CarWashCreateInputSerializer',
    'CarWashUpdateInputSerializer',
    'CarWashServicePriceUpsertInputSerializer',
    'CarWashServicePriceUpsertOutputSerializer',
    'CarWashUpdateOutputSerializer',
)


class CarWashListOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarWash
        fields = (
            'id',
            'name',
            'comfort_class_car_washing_price',
            'business_class_car_washing_price',
            'van_washing_price',
            'windshield_washer_price_per_bottle',
            'created_at',
            'updated_at',
        )


class CarWashRetrieveOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarWash
        fields = (
            'id',
            'name',
            'comfort_class_car_washing_price',
            'business_class_car_washing_price',
            'van_washing_price',
            'windshield_washer_price_per_bottle',
            'created_at',
            'updated_at',
        )


class CarWashUpdateInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    comfort_class_car_washing_price = serializers.IntegerField(min_value=0)
    business_class_car_washing_price = serializers.IntegerField(min_value=0)
    van_washing_price = serializers.IntegerField(min_value=0)
    windshield_washer_price_per_bottle = serializers.IntegerField(min_value=0)


class CarWashUpdateOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    comfort_class_car_washing_price = serializers.IntegerField()
    business_class_car_washing_price = serializers.IntegerField()
    van_washing_price = serializers.IntegerField()
    windshield_washer_price_per_bottle = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class CarWashCreateInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    comfort_class_car_washing_price = serializers.IntegerField(min_value=0)
    business_class_car_washing_price = serializers.IntegerField(min_value=0)
    van_washing_price = serializers.IntegerField(min_value=0)
    windshield_washer_price_per_bottle = serializers.IntegerField(min_value=0)


class CarWashCreateOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarWash
        fields = (
            'id',
            'name',
            'comfort_class_car_washing_price',
            'business_class_car_washing_price',
            'van_washing_price',
            'windshield_washer_price_per_bottle',
            'created_at',
            'updated_at',
        )


class CarWashServicePriceUpsertInputSerializer(serializers.Serializer):
    price = serializers.IntegerField(min_value=0, max_value=1_000_000)


class CarWashServicePriceUpsertOutputSerializer(serializers.Serializer):
    car_wash_id = serializers.IntegerField()
    service_id = serializers.UUIDField()
    price = serializers.IntegerField()
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
