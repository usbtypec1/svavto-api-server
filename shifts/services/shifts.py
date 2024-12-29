import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.utils import timezone

from shifts.exceptions import (
    ShiftAlreadyExistsError,
    ShiftNotFoundError,
    StaffHasActiveShiftError,
)
from shifts.models import Shift, ShiftFinishPhoto
from shifts.selectors import has_any_finished_shift
from staff.models import Staff

__all__ = (
    'create_shifts',
    'start_shift',
    'ensure_staff_has_no_active_shift',
    'ShiftFinishResult',
    'ShiftFinishInteractor',
    'get_shifts_by_staff_id',
    'delete_shift_by_id',
    'create_and_start_shifts',
    'ensure_shift_exists',
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
) -> list[Shift]:
    shifts = [
        Shift(
            staff=staff,
            date=date,
            is_extra=is_extra,
            created_at=timezone.now(),
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
) -> list[Shift]:
    now = timezone.now()
    shifts = [
        Shift(
            staff=staff,
            date=date,
            car_wash_id=car_wash_id,
            started_at=now,
            is_extra=is_extra,
            created_at=now,
        )
        for date in dates
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
            Shift.objects.select_related('car_wash', 'staff')
            .only('id', 'date', 'car_wash', 'staff')
            .get(id=shift_id)
        )
    except Shift.DoesNotExist:
        raise ShiftNotFoundError

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


@dataclass(frozen=True, slots=True)
class ShiftFinishResult:
    shift_id: int
    is_first_shift: bool
    staff_full_name: str
    car_numbers: tuple[str, ...]


class ShiftFinishInteractor:

    def __init__(self, shift: Shift, photo_file_ids: Iterable[str]):
        self.__shift = shift
        self.__photo_file_ids = tuple(photo_file_ids)

    def save_shift_finish_date(self) -> None:
        if self.__shift.finished_at is not None:
            return

        self.__shift.finished_at = timezone.now()
        self.__shift.save(update_fields=('finished_at',))

    def delete_shift_finish_photos(self) -> None:
        ShiftFinishPhoto.objects.filter(shift_id=self.__shift.id).delete()

    def create_shift_finish_photos(self) -> list[ShiftFinishPhoto]:
        finish_photos = [
            ShiftFinishPhoto(file_id=file_id, shift_id=self.__shift.id)
            for file_id in self.__photo_file_ids
        ]
        return ShiftFinishPhoto.objects.bulk_create(finish_photos)

    def get_car_numbers(self) -> tuple[str, ...]:
        return tuple(
            self.__shift
            .cartowash_set
            .values_list('number', flat=True)
        )

    def create_result(
            self,
            is_first_shift: bool,
            car_numbers: Iterable[str],
    ) -> ShiftFinishResult:
        return ShiftFinishResult(
            shift_id=self.__shift.id,
            is_first_shift=is_first_shift,
            staff_full_name=self.__shift.staff.full_name,
            car_numbers=tuple(car_numbers),
        )

    @transaction.atomic
    def finish_shift(self) -> ShiftFinishResult:
        is_first_shift = not has_any_finished_shift(self.__shift.staff_id)
        self.save_shift_finish_date()
        self.delete_shift_finish_photos()
        self.create_shift_finish_photos()
        car_numbers = self.get_car_numbers()

        return self.create_result(
            is_first_shift=is_first_shift,
            car_numbers=car_numbers,
        )


def get_shifts_by_staff_id(
        *,
        staff_id: int,
        month: int | None,
        year: int | None,
) -> QuerySet[Shift]:
    shifts = Shift.objects.select_related('car_wash').filter(staff_id=staff_id)
    if month is not None:
        shifts = shifts.filter(date__month=month)
    if year is not None:
        shifts = shifts.filter(date__year=year)
    return shifts


def delete_shift_by_id(shift_id: int) -> None:
    deleted_count, _ = Shift.objects.filter(id=shift_id).delete()
    if deleted_count == 0:
        raise ShiftNotFoundError


def ensure_shift_exists(shift_id: int) -> None:
    if not Shift.objects.filter(id=shift_id).exists():
        raise ShiftNotFoundError
