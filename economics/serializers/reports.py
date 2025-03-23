import datetime

from django.utils.translation import gettext as _
from rest_framework import serializers


__all__ = (
    "StaffItemSerializer",
    "ShiftStatisticsSerializer",
    "StaffShiftsStatisticsSerializer",
    "StaffShiftsStatisticsReportInputSerializer",
    "StaffShiftsStatisticsReportOutputSerializer",
    "CarWashesRevenueReportInputSerializer",
    "CarWashesRevenueReportOutputSerializer",
    "CarWashRevenueForShiftSerializer",
    "CarWashRevenueForShiftAdditionalServiceSerializer",
)

from shifts.serializers import ReportPeriodSerializer


class CarWashesRevenueReportInputSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    car_wash_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )

    def validate(self, data: dict) -> dict:
        from_date: datetime.date = data["from_date"]
        to_date: datetime.date = data["to_date"]

        if from_date > to_date:
            raise serializers.ValidationError(
                _("period end can not be before period start"),
            )

        period_duration = to_date - from_date
        period_duration_threshold = datetime.timedelta(days=60)

        if period_duration > period_duration_threshold:
            raise serializers.ValidationError(
                _("period duration can not be greater than 60 days"),
            )

        return data


class CarWashRevenueForShiftAdditionalServiceSerializer(
    serializers.Serializer
):
    id = serializers.UUIDField()
    name = serializers.CharField()
    count = serializers.IntegerField()


class CarWashRevenueForShiftSerializer(serializers.Serializer):
    shift_date = serializers.DateField()
    comfort_cars_washed_count = serializers.IntegerField()
    business_cars_washed_count = serializers.IntegerField()
    van_cars_washed_count = serializers.IntegerField()
    windshield_washer_refilled_bottle_count = serializers.IntegerField()
    total_cost = serializers.IntegerField()
    additional_services = serializers.ListField(
        child=CarWashRevenueForShiftAdditionalServiceSerializer(),
    )
    penalties_amount = serializers.IntegerField()
    surcharges_amount = serializers.IntegerField()


class CarWashesRevenueReportOutputSerializer(serializers.Serializer):
    car_washes_revenue = serializers.ListField(
        child=CarWashRevenueForShiftSerializer(),
    )


class StaffItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    car_sharing_phone_number = serializers.CharField()
    console_phone_number = serializers.CharField()
    created_at = serializers.DateTimeField()
    banned_at = serializers.DateTimeField(allow_null=True)


class ShiftStatisticsSerializer(serializers.Serializer):
    shift_date = serializers.DateField()
    penalty_amount = serializers.IntegerField()
    surcharge_amount = serializers.IntegerField()
    planned_comfort_cars_washed_count = serializers.IntegerField()
    planned_business_cars_washed_count = serializers.IntegerField()
    planned_vans_washed_count = serializers.IntegerField()
    urgent_cars_washed_count = serializers.IntegerField()
    is_extra_shift = serializers.BooleanField()
    dry_cleaning_items_count = serializers.IntegerField()
    washed_cars_total_cost = serializers.IntegerField()
    washed_cars_total_count = serializers.IntegerField()
    dirty_revenue = serializers.IntegerField()
    road_accident_deposit_amount = serializers.FloatField()


class TotalStatisticsSerializer(serializers.Serializer):
    penalty_amount = serializers.IntegerField()
    surcharge_amount = serializers.IntegerField()
    planned_comfort_cars_washed_count = serializers.IntegerField()
    planned_business_cars_washed_count = serializers.IntegerField()
    planned_vans_washed_count = serializers.IntegerField()
    urgent_cars_washed_count = serializers.IntegerField()
    extra_shifts_count = serializers.IntegerField()
    dry_cleaning_items_count = serializers.IntegerField()
    washed_cars_total_cost = serializers.IntegerField()
    washed_cars_total_count = serializers.IntegerField()
    dirty_revenue = serializers.IntegerField()
    road_accident_deposit_amount = serializers.FloatField()
    fine_deposit_amount = serializers.IntegerField()
    net_revenue = serializers.FloatField()


class StaffShiftsStatisticsSerializer(serializers.Serializer):
    staff = StaffItemSerializer()
    shifts_statistics = serializers.ListField(
        child=ShiftStatisticsSerializer(),
    )
    total_statistics = TotalStatisticsSerializer()


class StaffShiftsStatisticsReportInputSerializer(serializers.Serializer):
    year = serializers.IntegerField(min_value=2000, max_value=3000)
    month = serializers.IntegerField(min_value=1, max_value=12)
    report_period_number = serializers.IntegerField(min_value=1, max_value=2)
    staff_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_null=True,
        default=None,
    )


class StaffShiftsStatisticsReportOutputSerializer(serializers.Serializer):
    staff_list = serializers.ListField(
        child=StaffShiftsStatisticsSerializer(),
    )
    report_period = ReportPeriodSerializer()
