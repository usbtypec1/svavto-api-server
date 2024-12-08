from rest_framework import serializers

__all__ = (
    'SurchargeCreateInputSerializer',
    'SurchargeCreateOutputSerializer',
)


class SurchargeCreateInputSerializer(serializers.Serializer):
    shift_id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=255)
    amount = serializers.IntegerField(min_value=0)


class SurchargeCreateOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    shift_id = serializers.IntegerField()
    reason = serializers.CharField()
    amount = serializers.IntegerField()
    created_at = serializers.DateTimeField()
