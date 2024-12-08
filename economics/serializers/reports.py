from rest_framework import serializers

__all__ = ('ServiceCostsInputSerializer',)


class ServiceCostsInputSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    car_wash_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )
