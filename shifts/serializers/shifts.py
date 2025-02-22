from django.utils.translation import gettext_lazy as _
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
    'ShiftCreateOutputSerializer',
    'ShiftCreateItemSerializer',
    'CarWashSummarySerializer',
    'ShiftTestCreateInputSerializer',
    'ShiftTestCreateOutputSerializer',
    'ShiftExtraCreateOutputSerializer',
    'ShiftExtraCreateInputSerializer',
    'ShiftListV2InputSerializer',
    'ShiftListV2ItemSerializer',
    'ShiftListV2OutputSerializer',
    'ShiftRejectInputSerializer',
    'ShiftRejectOutputSerializer',
    'DeadSoulsInputSerializer',
    'DeadSoulsOutputSerializer',
    'StaffIdAndFullNameSerializer',
    'StaffIdAndDateSerializer',
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


class StaffIdAndDateSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    date = serializers.DateField()


class ShiftTestCreateInputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    date = serializers.DateField()


class ShiftExtraCreateInputSerializer(serializers.Serializer):
    shifts = serializers.ListField(
        child=StaffIdAndDateSerializer(),
        min_length=1,
    )


class ShiftCreateInputSerializer(serializers.Serializer):
    shifts = serializers.ListField(
        child=StaffIdAndDateSerializer(),
        min_length=1,
    )


class ShiftCreateItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    date = serializers.DateField()


class ShiftCreateOutputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    staff_full_name = serializers.CharField()
    shifts = serializers.ListField(child=ShiftCreateItemSerializer())


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
    trunk_vacuum_count = serializers.IntegerField()


class ShiftFinishOutputSerializer(serializers.Serializer):
    shift_id = serializers.IntegerField()
    is_first_shift = serializers.BooleanField()
    staff_id = serializers.IntegerField()
    staff_full_name = serializers.CharField()
    car_washes = serializers.ListSerializer(child=CarWashSummarySerializer())
    finish_photo_file_ids = serializers.ListField(
        child=serializers.CharField(),
    )


class ShiftTestCreateOutputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    staff_full_name = serializers.CharField()
    shift_id = serializers.IntegerField()
    shift_date = serializers.DateField()


class ShiftExtraCreateOutputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    staff_full_name = serializers.CharField()
    shift_id = serializers.IntegerField()
    shift_date = serializers.DateField()


class ShiftListV2InputSerializer(serializers.Serializer):
    staff_ids = serializers.ListField(
        child=serializers.IntegerField(),
        default=None,
        max_length=100,
        min_length=1
    )
    from_date = serializers.DateField(default=None, allow_null=True)
    to_date = serializers.DateField(default=None, allow_null=True)
    limit = serializers.IntegerField(default=50, min_value=1, max_value=1000)
    offset = serializers.IntegerField(default=0, min_value=0)
    types = serializers.MultipleChoiceField(choices=Shift.Type.choices)

    def validate(self, attrs):
        if attrs['from_date'] is not None and attrs['to_date'] is not None:
            if attrs['from_date'] > attrs['to_date']:
                raise serializers.ValidationError(
                    _('from_date should be less than or equal to to_date')
                )
        return attrs


class ShiftListV2ItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    date = serializers.DateField()
    car_wash_id = serializers.IntegerField(allow_null=True)
    car_wash_name = serializers.CharField(allow_null=True)
    staff_id = serializers.IntegerField(allow_null=True)
    staff_full_name = serializers.CharField(allow_null=True)
    started_at = serializers.DateTimeField(allow_null=True)
    finished_at = serializers.DateTimeField(allow_null=True)
    rejected_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    type = serializers.ChoiceField(choices=Shift.Type.choices)


class ShiftListV2OutputSerializer(serializers.Serializer):
    shifts = serializers.ListSerializer(child=ShiftListV2ItemSerializer())
    is_end_of_list_reached = serializers.BooleanField()


class ShiftRejectInputSerializer(serializers.Serializer):
    shift_id = serializers.IntegerField()


class ShiftRejectOutputSerializer(serializers.Serializer):
    pass


class DeadSoulsInputSerializer(serializers.Serializer):
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=2000, max_value=2100)


class StaffIdAndFullNameSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()


class DeadSoulsOutputSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    staff_list = serializers.ListSerializer(
        child=StaffIdAndFullNameSerializer(),
    )
