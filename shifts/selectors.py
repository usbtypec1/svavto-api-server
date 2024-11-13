import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from shifts.exceptions import ShiftNotFoundError, StaffHasNoActiveShiftError
from shifts.models import Shift

__all__ = (
    'get_staff_ids_by_shift_date',
    'get_staff_ids_by_shift_ids',
    'get_shift_by_id',
    'get_staff_current_shift',
    'has_any_finished_shift',
)


@dataclass(frozen=True, slots=True)
class ShiftIdAndStaffId:
    shift_id: int
    staff_id: int


@dataclass(frozen=True, slots=True)
class ShiftIdAndStaffFullName:
    shift_id: int
    staff_id: int
    staff_full_name: str


def get_shift_by_id(
        shift_id: int,
) -> Shift:
    try:
        return (
            Shift.objects
            .select_related('staff', 'car_wash')
            .get(id=shift_id)
        )
    except Shift.DoesNotExist:
        raise ShiftNotFoundError


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


def get_staff_current_shift(staff_id: int) -> Shift:
    try:
        return Shift.objects.get(
            staff_id=staff_id,
            started_at__isnull=False,
            finished_at__isnull=True,
        )
    except Shift.DoesNotExist:
        raise StaffHasNoActiveShiftError


def has_any_finished_shift(staff_id: int) -> bool:
    return Shift.objects.filter(
        staff_id=staff_id,
        finished_at__isnull=False
    ).exists()
