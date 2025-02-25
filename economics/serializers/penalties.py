from rest_framework import serializers

from economics.models import Penalty


__all__ = (
    'PenaltyCreateInputSerializer',
    'PenaltyCreateOutputSerializer',
    'PenaltyListOutputSerializer',
    'PenaltyListInputSerializer',
    'PenaltyListItemSerializer',
)


class PenaltyCreateInputSerializer(serializers.Serializer):
    shift_id = serializers.IntegerField()
    reason = serializers.CharField(max_length=255)
    amount = serializers.IntegerField(
        min_value=0,
        allow_null=True,
        default=None,
    )
    photo_urls = serializers.ListField(
        child=serializers.URLField(),
        default=list,
    )


class PenaltyCreateOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    staff_full_name = serializers.CharField()
    shift_id = serializers.IntegerField()
    shift_date = serializers.DateField()
    reason = serializers.CharField()
    amount = serializers.IntegerField()
    consequence = serializers.ChoiceField(
        choices=Penalty.Consequence.choices,
        allow_null=True,
    )
    created_at = serializers.DateTimeField()


class PenaltyListInputSerializer(serializers.Serializer):
    staff_ids = serializers.ListField(
        child=serializers.IntegerField(),
        default=None,
    )
    limit = serializers.IntegerField(min_value=1, max_value=1000, default=10)
    offset = serializers.IntegerField(min_value=0, default=0)


class PenaltyListItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    staff_full_name = serializers.CharField()
    shift_id = serializers.IntegerField()
    shift_date = serializers.DateField()
    reason = serializers.CharField()
    consequence = serializers.ChoiceField(
        choices=Penalty.Consequence.choices,
        allow_null=True,
    )
    amount = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class PenaltyListOutputSerializer(serializers.Serializer):
    penalties = PenaltyListItemSerializer(many=True)
    is_end_of_list_reached = serializers.BooleanField()
