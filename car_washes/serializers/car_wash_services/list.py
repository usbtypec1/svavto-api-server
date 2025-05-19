from rest_framework import serializers


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
