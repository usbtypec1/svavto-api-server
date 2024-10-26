import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from shifts.models import Shift

__all__ = (
    'get_staff_ids_by_shift_date',
    'get_staff_ids_by_shift_ids',
    'get_staff_list_by_shift_date',
)


@dataclass(frozen=True, slots=True)
class ShiftIdAndStaffId:
    shift_id: int
    staff_id: int


@dataclass(frozen=True, slots=True)
class ShiftIdAndStaffFullName:
    shift_id: int
    staff_full_name: str


def get_staff_list_by_shift_date(
        date: datetime.date,
) -> list[ShiftIdAndStaffFullName]:
    shifts = (
        Shift.objects
        .select_related('shift')
        .filter(date=date)
        .values('id', 'staff__full_name')
    )
    return [
        ShiftIdAndStaffFullName(
            shift_id=shift['id'],
            staff_full_name=shift['staff__full_name'],
        )
        for shift in shifts
    ]


def get_staff_ids_by_shift_date(date: datetime.date) -> list[ShiftIdAndStaffId]:
    shifts = Shift.objects.filter(date=date).values('id', 'staff_id')
    return [
        ShiftIdAndStaffId(
            shift_id=shift['id'],
            staff_id=shift['staff_id'],
        )
        for shift in shifts
    ]


def get_staff_ids_by_shift_ids(
        shift_ids: Iterable[int],
) -> list[ShiftIdAndStaffId]:
    shifts = (
        Shift.objects
        .filter(id__in=shift_ids)
        .values('id', 'staff_id')
    )
    return [
        ShiftIdAndStaffId(
            shift_id=shift['id'],
            staff_id=shift['staff_id'],
        )
        for shift in shifts
    ]
