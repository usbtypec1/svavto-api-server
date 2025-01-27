from rest_framework import serializers

from shifts.models import Shift

__all__ = (
    'ShiftListForSpecificDateOutputSerializer',
    'StaffCurrentShiftRetrieveOutputSerializer',
    'ShiftListInputSerializer',
    'ShiftCreateInputSerializer',
    'ShiftRetrieveOutputSerializer',
    'ShiftListOutputSerializer',
    'ShiftFinishOutputSerializer',
    'ShiftFinishInputSerializer',
)


class ShiftListForSpecificDateOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = (
            'id',
            'date',
            'staff',
            'is_started',
            'is_finished',
            'created_at',
        )
        depth = 1


class ShiftRetrieveOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = (
            'id',
            'date',
            'car_wash',
            'staff',
            'is_started',
            'is_finished',
            'created_at',
        )
        depth = 1


class StaffCurrentShiftRetrieveOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = (
            'id',
            'date',
            'car_wash',
            'staff',
            'is_started',
            'is_finished',
            'created_at',
        )
        depth = 1


class ShiftListInputSerializer(serializers.Serializer):
    date_from = serializers.DateField(default=None, allow_null=True)
    date_to = serializers.DateField(default=None, allow_null=True)
    staff_ids = serializers.ListField(
        child=serializers.IntegerField(),
        default=None,
        allow_null=True,
        allow_empty=False,
    )
    limit = serializers.IntegerField(default=10, min_value=1, max_value=1000)
    offset = serializers.IntegerField(default=0, min_value=0)


class ShiftListOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = (
            'id',
            'date',
            'car_wash',
            'staff',
            'is_started',
            'is_finished',
            'created_at',
        )
        depth = 1


class ShiftCreateInputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    dates = serializers.ListField(child=serializers.DateField())
    immediate_start = serializers.BooleanField(default=False)
    car_wash_id = serializers.IntegerField(default=None, allow_null=True)
    is_extra = serializers.BooleanField(default=False)
    is_test = serializers.BooleanField(default=False)

    def validate(self, data: dict) -> dict:
        if data['immediate_start'] and 'car_wash_id' not in data:
            raise serializers.ValidationError(
                'car_wash_id is required for immediate_start',
            )
        return data


class ShiftFinishInputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    photo_file_ids = serializers.ListField(
        child=serializers.CharField(
            max_length=255,
        ),
    )


class CarWashSummarySerializer(serializers.Serializer):
    car_wash_id = serializers.IntegerField()
    car_wash_name = serializers.CharField()
    comfort_cars_count = serializers.IntegerField()
    business_cars_count = serializers.IntegerField()
    vans_count = serializers.IntegerField()
    planned_cars_count = serializers.IntegerField()
    urgent_cars_count = serializers.IntegerField()
    dry_cleaning_count = serializers.IntegerField()
    total_cars_count = serializers.IntegerField()
    refilled_cars_count = serializers.IntegerField()
    not_refilled_cars_count = serializers.IntegerField()


class ShiftFinishOutputSerializer(serializers.Serializer):
    shift_id = serializers.IntegerField()
    is_first_shift = serializers.BooleanField()
    staff_id = serializers.IntegerField()
    staff_full_name = serializers.CharField()
    car_washes = serializers.ListSerializer(child=CarWashSummarySerializer())
    finish_photo_file_ids = serializers.ListField(
        child=serializers.CharField(),
    )
