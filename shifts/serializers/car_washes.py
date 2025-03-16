from rest_framework import serializers

from car_washes.models import CarWash

__all__ = ("CarWashSerializer",)


class CarWashSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarWash
        fields = ("id", "name")
