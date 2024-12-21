from rest_framework import serializers

__all__ = (
    'ServiceCostsInputSerializer',
    'StaffItemSerializer',
    'ShiftStatisticsSerializer',
    'StaffShiftsStatisticsSerializer',
    'StaffShiftsStatisticsReportInputSerializer',
    'StaffShiftsStatisticsReportOutputSerializer',
    'CarWashesRevenueReportOutputSerializer',
    'CarWashRevenueForShiftSerializer',
    'CarWashRevenueForShiftAdditionalServiceSerializer',
)


class ServiceCostsInputSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    car_wash_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )


class CarWashRevenueForShiftAdditionalServiceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    count = serializers.IntegerField()
    total_price = serializers.IntegerField()


class CarWashRevenueForShiftSerializer(serializers.Serializer):
    car_wash_id = serializers.IntegerField()
    car_wash_name = serializers.CharField()
    shift_date = serializers.DateField()
    comfort_cars_washed_count = serializers.IntegerField()
    business_cars_washed_count = serializers.IntegerField()
    van_cars_washed_count = serializers.IntegerField()
    windshield_washer_refilled_bottle_count = serializers.IntegerField()
    total_cost = serializers.IntegerField()
    additional_services = serializers.ListField(
        child=CarWashRevenueForShiftAdditionalServiceSerializer(),
    )


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
    washed_cars_total_cost = serializers.IntegerField()


class StaffShiftsStatisticsSerializer(serializers.Serializer):
    staff = StaffItemSerializer()
    shifts_statistics = serializers.ListField(
        child=ShiftStatisticsSerializer(),
    )


class StaffShiftsStatisticsReportInputSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    staff_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_null=True,
        default=None,
    )


class StaffShiftsStatisticsReportOutputSerializer(serializers.Serializer):
    staff_list = serializers.ListField(
        child=StaffShiftsStatisticsSerializer(),
    )
