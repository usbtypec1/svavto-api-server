import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from shifts.exceptions import (
    ShiftByDateNotFoundError,
    ShiftNotConfirmedError,
    StaffHasActiveShiftError,
)
from shifts.models import Shift

__all__ = (
    'create_unconfirmed_shifts',
    'confirm_shifts',
    'start_shift',
    'ensure_staff_has_no_active_shift',
)


@dataclass(frozen=True, slots=True)
class ShiftDTO:
    id: int
    performer_telegram_id: int
    date: datetime.date


def create_unconfirmed_shifts(
        performer_id: int,
        dates: Iterable[datetime.date],
) -> list[ShiftDTO]:
    shifts = [
        Shift(performer_id=performer_id, date=date)
        for date in dates
    ]
    shifts = Shift.objects.bulk_create(shifts)
    return [
        ShiftDTO(
            id=shift.id,
            performer_telegram_id=shift.performer_id,
            date=shift.date,
        )
        for shift in shifts
    ]


def confirm_shifts(shift_ids: Iterable[int]):
    Shift.objects.filter(id__in=shift_ids).update(is_confirmed=True)


def start_shift(
        *,
        staff_id: int,
        date: datetime.date,
        car_wash_id: int,
) -> Shift:
    try:
        shift = (
            Shift.objects
            .select_related('car_wash', 'staff')
            .only('id', 'date', 'car_wash', 'staff')
            .get(
                staff_id=staff_id,
                date=date,
            )
        )
    except Shift.DoesNotExist:
        raise ShiftByDateNotFoundError

    if not shift.is_confirmed:
        raise ShiftNotConfirmedError

    if shift.is_active:
        raise StaffHasActiveShiftError

    shift.is_active = True
    shift.car_wash_id = car_wash_id
    shift.save(update_fields=('is_active', 'car_wash_id'))

    return shift


def ensure_staff_has_no_active_shift(
        staff_id: int,
) -> None:
    if Shift.objects.filter(staff_id=staff_id, is_active=True).exists():
        raise StaffHasActiveShiftError
