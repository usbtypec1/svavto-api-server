from rest_framework import serializers

from car_washes.models import CarWash, CarWashService

__all__ = (
    'CarWashListOutputSerializer',
    'CarWashRetrieveOutputSerializer',
    'CarWashServiceSerializer',
    'CarWashCreateOutputSerializer',
    'CarWashCreateInputSerializer',
)


class CarWashListOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarWash
        fields = ('id', 'name', 'created_at', 'updated_at')


class CarWashServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarWashService
        fields = ('id', 'name', 'price', 'created_at', 'updated_at')


class CarWashRetrieveOutputSerializer(serializers.ModelSerializer):
    services = CarWashServiceSerializer(many=True)

    class Meta:
        model = CarWash
        fields = ('id', 'name', 'created_at', 'updated_at', 'services')


class CarWashUpdateInputSerializer(serializers.Serializer):
    class Meta:
        model = CarWash
        fields = ('name',)


class CarWashCreateInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class CarWashCreateOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarWash
        fields = ('id', 'name', 'created_at', 'updated_at')
