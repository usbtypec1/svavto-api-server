from rest_framework import serializers

from economics.models import CarTransporterPenalty


__all__ = (
    "CarTransporterPenaltyCreateInputSerializer",
    "PenaltyCreateOutputSerializer",
    "PenaltyListOutputSerializer",
    "PenaltyListInputSerializer",
    "PenaltyListItemSerializer",
)


class CarTransporterPenaltyCreateInputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    date = serializers.DateField()
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
    date = serializers.DateField()
    reason = serializers.CharField()
    amount = serializers.IntegerField()
    consequence = serializers.ChoiceField(
        choices=CarTransporterPenalty.Consequence.choices,
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
    date = serializers.DateField()
    reason = serializers.CharField()
    consequence = serializers.ChoiceField(
        choices=CarTransporterPenalty.Consequence.choices,
        allow_null=True,
    )
    amount = serializers.IntegerField()
    photo_urls = serializers.ListSerializer(child=serializers.URLField())
    created_at = serializers.DateTimeField()


class PenaltyListOutputSerializer(serializers.Serializer):
    penalties = PenaltyListItemSerializer(many=True)
    is_end_of_list_reached = serializers.BooleanField()
