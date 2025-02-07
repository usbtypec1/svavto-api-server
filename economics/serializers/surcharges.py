from rest_framework import serializers

__all__ = (
    'SurchargeCreateInputSerializer',
    'SurchargeCreateOutputSerializer',
    'SurchargeListOutputSerializer',
    'SurchargeListInputSerializer',
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


class SurchargeListInputSerializer(serializers.Serializer):
    staff_ids = serializers.ListField(
        child=serializers.IntegerField(),
        default=None,
        allow_null=True,
        allow_empty=False,
    )
    limit = serializers.IntegerField(min_value=1, max_value=1000, default=10)
    offset = serializers.IntegerField(min_value=0, default=0)


class SurchargeListOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    reason = serializers.CharField()
    amount = serializers.IntegerField()
    created_at = serializers.DateTimeField()
