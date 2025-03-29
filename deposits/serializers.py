from rest_framework import serializers

from shifts.serializers import ReportPeriodSerializer


class DepositListInputSerializer(serializers.Serializer):
    from_report_period_year = serializers.IntegerField()
    from_report_period_month = serializers.IntegerField(
        min_value=1,
        max_value=12,
    )
    from_report_period_number = serializers.IntegerField(
        min_value=1,
        max_value=2,
    )
    to_report_period_year = serializers.IntegerField()
    to_report_period_month = serializers.IntegerField(
        min_value=1,
        max_value=12,
    )
    to_report_period_number = serializers.IntegerField(
        min_value=1,
        max_value=2,
    )


class StaffItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    console_phone_number = serializers.CharField()
    car_sharing_phone_number = serializers.CharField()
    banned_at = serializers.DateField(allow_null=True)
    return_deposit_at = serializers.DateField(allow_null=True)
    total_fine_deposit_amount = serializers.IntegerField()
    total_road_accident_deposit_amount = serializers.FloatField()


class StaffDepositBreakdownItemSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    fine_deposit_amount = serializers.IntegerField()
    road_accident_deposit_amount = serializers.FloatField()


class DepositListItemSerializer(serializers.Serializer):
    report_period = ReportPeriodSerializer()
    staff_deposits_breakdown = serializers.ListField(
        child=StaffDepositBreakdownItemSerializer(),
    )


class DepositListOutputSerializer(serializers.Serializer):
    staff_list = serializers.ListField(child=StaffItemSerializer())
    deposits = serializers.ListField(child=DepositListItemSerializer())
