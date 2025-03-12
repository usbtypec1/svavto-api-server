import re

from rest_framework import serializers
from django.core.exceptions import ValidationError

from shifts.models.dry_cleaning_requests import DryCleaningRequest


def validate_car_number(car_number: str) -> None:
    pattern = r'^[А-Яа-я]\d{3}[А-Яа-я]{2}\d{3}$'
    if not bool(re.fullmatch(pattern, car_number)):
        raise ValidationError('Expected car number format: "А123БВ456"')


class DryCleaningRequestServiceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    count = serializers.IntegerField()


class DryCleaningRequestCreateInputSerializer(serializers.Serializer):
    shift_id = serializers.IntegerField()
    car_number = serializers.CharField(
        max_length=16,
        validators=(validate_car_number,),
    )
    photo_file_ids = serializers.ListField(
        child=serializers.CharField(max_length=255),
    )
    services = serializers.ListField(
        child=DryCleaningRequestServiceSerializer(),
        min_length=1,
    )


class DryCleaningRequestListInputSerializer(serializers.Serializer):
    shift_ids = serializers.ListField(
        child=serializers.IntegerField(),
        default=None,
    )


class DryCleaningRequestServiceOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    count = serializers.IntegerField()
    is_countable = serializers.BooleanField()


class DryCleaningRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    shift_id = serializers.IntegerField()
    car_number = serializers.CharField()
    photo_file_ids = serializers.ListField(child=serializers.CharField())
    services = DryCleaningRequestServiceOutputSerializer(many=True)
    status = serializers.ChoiceField(choices=DryCleaningRequest.Status.choices)
    response_comment = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class DryCleaningRequestApproveInputSerializer(serializers.Serializer):
    response_comment = serializers.CharField(allow_null=True)
    services = serializers.ListField(
        child=DryCleaningRequestServiceSerializer(),
        min_length=1,
    )


class DryCleaningRequestRejectInputSerializer(serializers.Serializer):
    response_comment = serializers.CharField(allow_null=True)
