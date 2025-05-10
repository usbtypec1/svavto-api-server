from rest_framework import serializers

from staff.models import StaffType


class StaffRegisterRequestRejectInputSerializer(serializers.Serializer):
    staff_register_request_id = serializers.IntegerField()


class StaffRegisterRequestAcceptInputSerializer(serializers.Serializer):
    staff_register_request_id = serializers.IntegerField()


class StaffRegisterRequestCreateInputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    full_name = serializers.CharField(max_length=255)
    car_sharing_phone_number = serializers.CharField(max_length=32)
    console_phone_number = serializers.CharField(max_length=32)
    staff_type = serializers.ChoiceField(choices=StaffType.choices)


class StaffRegisterRequestListCreateOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    full_name = serializers.CharField(max_length=255)
    car_sharing_phone_number = serializers.CharField(max_length=32)
    console_phone_number = serializers.CharField(max_length=32)
    staff_type = serializers.ChoiceField(choices=StaffType.choices)
    created_at = serializers.DateTimeField()
