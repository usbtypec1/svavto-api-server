from rest_framework import serializers

from staff.models import AdminStaff, Staff

__all__ = (
    'StaffListOutputSerializer',
    'StaffListInputSerializer',
    'StaffCreateInputSerializer',
    'StaffRetrieveOutputSerializer',
    'AdminStaffListSerializer',
)


class StaffCreateInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = (
            'id',
            'full_name',
            'car_sharing_phone_number',
            'console_phone_number',
        )


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


class StaffListOutputSerializer(serializers.ModelSerializer):
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
