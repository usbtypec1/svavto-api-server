from rest_framework import serializers

from staff.models import AdminStaff, Staff

__all__ = (
    'StaffListOutputSerializer',
    'StaffListInputSerializer',
    'StaffRetrieveOutputSerializer',
    'AdminStaffListSerializer',
    'StaffRegisterRequestListCreateOutputSerializer',
    'StaffRegisterRequestCreateInputSerializer',
    'StaffRegisterRequestAcceptInputSerializer',
    'StaffItemSerializer',
    'StaffRegisterRequestRejectInputSerializer',
)


class StaffRegisterRequestRejectInputSerializer(serializers.Serializer):
    staff_register_request_id = serializers.IntegerField()


class StaffRegisterRequestAcceptInputSerializer(serializers.Serializer):
    staff_register_request_id = serializers.IntegerField()


class StaffRegisterRequestCreateInputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    full_name = serializers.CharField(max_length=255)
    car_sharing_phone_number = serializers.CharField(max_length=32)
    console_phone_number = serializers.CharField(max_length=32)


class StaffRegisterRequestListCreateOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    full_name = serializers.CharField(max_length=255)
    car_sharing_phone_number = serializers.CharField(max_length=32)
    console_phone_number = serializers.CharField(max_length=32)
    created_at = serializers.DateTimeField()


class StaffListInputSerializer(serializers.Serializer):
    order_by = serializers.ChoiceField(
        choices=(
            'full_name',
            '-full_name',
            'created_at',
            '-created_at',
            'last_activity_at',
            '-last_activity_at',
        ),
        default='full_name',
    )
    include_banned = serializers.BooleanField(default=False)
    limit = serializers.IntegerField(min_value=1, max_value=1000, default=100)
    offset = serializers.IntegerField(min_value=0, default=0)


class StaffItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField(max_length=255)
    car_sharing_phone_number = serializers.CharField(max_length=255)
    console_phone_number = serializers.CharField(max_length=255)
    banned_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    last_activity_at = serializers.DateTimeField()


class PaginationSerializer(serializers.Serializer):
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
    total_count = serializers.IntegerField()


class StaffListOutputSerializer(serializers.Serializer):
    staff = serializers.ListSerializer(child=StaffItemSerializer())
    pagination = PaginationSerializer()


class StaffRetrieveOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = (
            'id',
            'full_name',
            'car_sharing_phone_number',
            'console_phone_number',
            'banned_at',
            'created_at',
            'last_activity_at',
        )


class AdminStaffListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminStaff
        fields = ('id', 'name')
