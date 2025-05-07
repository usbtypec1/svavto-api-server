from rest_framework import serializers

from staff.models import AdminStaff


class AdminStaffListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminStaff
        fields = ("id", "name")
