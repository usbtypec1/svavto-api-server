from rest_framework import serializers

__all__ = (
    "CarWashPenaltyCreateInputSerializer",
    "CarWashPenaltyListCreateOutputSerializer",
    "CarWashPenaltyListInputSerializer",
)


class CarWashPenaltyListInputSerializer(serializers.Serializer):
    from_date = serializers.DateField(default=None)
    to_date = serializers.DateField(default=None)
    car_wash_ids = serializers.ListField(
        child=serializers.IntegerField(),
        default=None,
    )


class CarWashPenaltyCreateInputSerializer(serializers.Serializer):
    car_wash_id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=1024)
    date = serializers.DateField()


class CarWashPenaltyListCreateOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    car_wash_id = serializers.IntegerField()
    amount = serializers.IntegerField()
    reason = serializers.CharField()
    date = serializers.DateField()
    created_at = serializers.DateTimeField()
