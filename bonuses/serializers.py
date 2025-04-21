from rest_framework import serializers


class BonusesExcludedStaffInputSerializer(serializers.Serializer):
    staff_ids = serializers.ListSerializer(
        child=serializers.IntegerField(),
    )
