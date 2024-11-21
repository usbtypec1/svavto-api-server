import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from django.db import IntegrityError
from django.db.models import QuerySet
from django.utils import timezone

from shifts.exceptions import (
    ShiftAlreadyExistsError, ShiftAlreadyFinishedError,
    ShiftNotConfirmedError,
    ShiftNotFoundError,
    StaffHasActiveShiftError,
)
from shifts.models import Shift
from shifts.selectors import has_any_finished_shift
from staff.models import Staff

__all__ = (
    'create_shifts',
    'start_shift',
    'ensure_staff_has_no_active_shift',
    'finish_shift',
    'get_shifts_by_staff_id',
    'delete_shift_by_id',
    'create_and_start_shifts',
)


@dataclass(frozen=True, slots=True)
class ShiftDTO:
    id: int
    performer_telegram_id: int
    date: datetime.date


def create_shifts(
        *,
        staff: Staff,
        dates: Iterable[datetime.date],
        is_extra: bool,
) -> QuerySet[Shift]:
    shifts = [
        Shift(
            staff=staff,
            date=date,
            is_extra=is_extra,
        )
        for date in dates
    ]
    try:
        return Shift.objects.bulk_create(shifts)
    except IntegrityError:
        raise ShiftAlreadyExistsError


def create_and_start_shifts(
        *,
        staff: Staff,
        dates: Iterable[datetime.date],
        car_wash_id: int,
        is_extra: bool,
) -> QuerySet[Shift]:
    now = timezone.now()
    shifts = [
        Shift(
            staff=staff,
            date=date,
            car_wash_id=car_wash_id,
            started_at=now,
            is_extra=is_extra,
        ) for date in dates
    ]
    try:
        return Shift.objects.bulk_create(shifts)
    except IntegrityError:
        raise ShiftAlreadyExistsError


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
        raise ShiftNotFoundError

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
    if Shift.objects.filter(
            staff_id=staff_id,
            finished_at__isnull=True,
    ).exists():
        raise StaffHasActiveShiftError


def finish_shift(
        *,
        shift: Shift,
        statement_photo_file_id: str,
        service_app_photo_file_id: str,
) -> dict:
    if shift.finished_at is not None:
        raise ShiftAlreadyFinishedError

    is_first_shift = not has_any_finished_shift(shift.staff_id)

    shift.finished_at = timezone.now()
    shift.statement_photo_file_id = statement_photo_file_id
    shift.service_app_photo_file_id = service_app_photo_file_id

    shift.full_clean()
    shift.save(
        update_fields=(
            'finished_at',
            'statement_photo_file_id',
            'service_app_photo_file_id',
        ),
    )

    return {
        'is_first_shift': is_first_shift,
        'staff_full_name': shift.staff.full_name,
        'car_numbers': shift.cartowash_set.values_list('number', flat=True),
    }


def get_shifts_by_staff_id(
        *,
        staff_id: int,
        month: int | None,
        year: int | None,
) -> QuerySet[Shift]:
    shifts = (
        Shift.objects
        .select_related('car_wash')
        .filter(staff_id=staff_id)
    )
    if month is not None:
        shifts = shifts.filter(date__month=month)
    if year is not None:
        shifts = shifts.filter(date__year=year)
    return shifts


def delete_shift_by_id(shift_id: int) -> None:
    deleted_count, _ = Shift.objects.filter(id=shift_id).delete()
    if deleted_count == 0:
        raise ShiftNotFoundError
