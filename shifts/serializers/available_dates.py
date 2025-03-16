from rest_framework import serializers

from shifts.models import AvailableDate

__all__ = ("AvailableDateSerializer", "DateSerializer")


class AvailableDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableDate
        fields = ("id", "month", "year")


class DateSerializer(serializers.Serializer):
    date = serializers.DateField()
