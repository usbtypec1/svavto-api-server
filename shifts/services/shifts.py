import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from django.utils import timezone

from shifts.exceptions import (
    ShiftAlreadyConfirmedError, ShiftAlreadyFinishedError,
    ShiftByDateNotFoundError,
    ShiftNotConfirmedError,
    StaffHasActiveShiftError,
    StaffHasNoActiveShiftError,
)
from shifts.models import CarToWash, Shift

__all__ = (
    'create_unconfirmed_shifts',
    'confirm_shift',
    'start_shift',
    'ensure_staff_has_no_active_shift',
    'finish_shift',
)

from shifts.selectors import has_any_finished_shift


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


def confirm_shift(
        *,
        date: datetime.date,
        staff_id: int,
) -> None:
    try:
        shift = Shift.objects.get(date=date, staff_id=staff_id)
    except Shift.DoesNotExist:
        raise ShiftByDateNotFoundError

    if shift.is_confirmed:
        raise ShiftAlreadyConfirmedError

    shift.confirmed_at = timezone.now()
    shift.save(update_fields=('confirmed_at',))


def start_shift(
        *,
        shift_id: int,
        car_wash_id: int,
) -> Shift:
    try:
        shift = (
            Shift.objects
            .select_related('car_wash', 'staff')
            .only('id', 'date', 'car_wash', 'staff')
            .get(id=shift_id)
        )
    except Shift.DoesNotExist:
        raise ShiftByDateNotFoundError

    if not shift.is_confirmed:
        raise ShiftNotConfirmedError

    if shift.is_started:
        raise StaffHasActiveShiftError

    shift.started_at = timezone.now()
    shift.car_wash_id = car_wash_id
    shift.save(update_fields=('started_at', 'car_wash_id'))

    return shift


def ensure_staff_has_no_active_shift(
        staff_id: int,
) -> None:
    if Shift.objects.filter(staff_id=staff_id, is_active=True).exists():
        raise StaffHasActiveShiftError


def finish_shift(shift: Shift) -> dict:
    if shift.finished_at is not None:
        raise ShiftAlreadyFinishedError

    is_first_shift = not has_any_finished_shift(shift.staff_id)

    shift.finished_at = timezone.now()
    shift.save(update_fields=('finished_at',))

    return {
        'is_first_shift': is_first_shift,
        'staff_full_name': shift.staff.full_name,
        'car_numbers': shift.cartowash_set.values_list('number', flat=True),
    }
