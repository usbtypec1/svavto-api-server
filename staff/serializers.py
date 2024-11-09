from rest_framework import serializers

from staff.models import Staff

__all__ = (
    'StaffListOutputSerializer',
    'StaffListInputSerializer',
    'StaffCreateInputSerializer',
    'StaffRetrieveOutputSerializer',
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
            'is_banned',
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
            'is_banned',
            'created_at',
            'last_activity_at',
        )
