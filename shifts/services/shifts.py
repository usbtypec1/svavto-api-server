import collections
import datetime
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache

from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.utils import timezone

from shifts.exceptions import (
    ShiftAlreadyExistsError,
    ShiftNotFoundError,
    StaffHasActiveShiftError,
)
from shifts.models import (
    CarToWash, CarToWashAdditionalService, Shift,
    ShiftFinishPhoto,
)
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
        is_test: bool,
) -> list[Shift]:
    shifts = [
        Shift(
            staff=staff,
            date=date,
            is_extra=is_extra,
            is_test=is_test,
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
        is_test: bool,
) -> list[Shift]:
    now = timezone.now()
    shifts = [
        Shift(
            staff=staff,
            date=date,
            car_wash_id=car_wash_id,
            started_at=now,
            is_extra=is_extra,
            is_test=is_test,
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
class ShiftSummary:
    staff_full_name: str
    car_wash_name: str
    comfort_cars_count: int
    business_cars_count: int
    vans_count: int
    planned_cars_count: int
    urgent_cars_count: int
    dry_cleaning_count: int
    total_cars_count: int
    refilled_cars_count: int
    not_refilled_cars_count: int
    finish_photo_file_ids: list[str]


@dataclass(frozen=True, slots=True)
class ShiftFinishResult(ShiftSummary):
    shift_id: int
    is_first_shift: bool
    car_numbers: tuple[str, ...]


class ShiftSummaryInteractor:

    def __init__(self, shift_id: int):
        self.__shift_id = shift_id

    @lru_cache
    def get_shift(self) -> Shift:
        return (
            Shift.objects
            .select_related('staff', 'car_wash')
            .get(id=self.__shift_id)
        )

    @lru_cache
    def get_cars_to_wash(self) -> QuerySet[CarToWash]:
        return CarToWash.objects.filter(shift=self.get_shift())

    @lru_cache
    def get_additional_services(self) -> QuerySet[CarToWashAdditionalService]:
        return (
            CarToWashAdditionalService.objects
            .filter(car__in=self.get_cars_to_wash())
            .select_related('service')
            .all()
        )

    def get_photo_file_ids(self) -> list[str]:
        return list(
            self.get_shift()
            .finish_photos
            .values_list('file_id', flat=True)
        )

    def get_refilled_cars_count(self) -> int:
        count: int = 0
        for car_to_wash in self.get_cars_to_wash():
            if car_to_wash.windshield_washer_refilled_bottle_percentage != 0:
                count += (
                    car_to_wash.windshield_washer_refilled_bottle_percentage
                )
        return count

    def get_dry_cleaning_items_count(self) -> int:
        count: int = 0
        for additional_service in self.get_additional_services():
            if additional_service.service.is_dry_cleaning:
                count += 1
        return count

    def get_car_class_to_count(self) -> dict[CarToWash.CarType, int]:
        car_class_to_count = collections.defaultdict(int)
        for car_to_wash in self.get_cars_to_wash():
            car_class_to_count[car_to_wash.car_class] += 1
        return car_class_to_count

    def get_wash_type_to_count(self) -> dict[CarToWash.WashType, int]:
        wash_type_to_count = collections.defaultdict(int)
        for car_to_wash in self.get_cars_to_wash():
            wash_type_to_count[car_to_wash.wash_type] += 1
        return wash_type_to_count

    def get_car_wash_name(self) -> str | None:
        shift = self.get_shift()
        if shift.car_wash is None:
            return None
        return shift.car_wash.name

    def get_shift_summary(self) -> ShiftSummary:
        shift = self.get_shift()
        car_wash_name = self.get_car_wash_name()
        dry_cleaning_items_count = self.get_dry_cleaning_items_count()
        wash_type_to_count = self.get_wash_type_to_count()
        car_class_to_count = self.get_car_class_to_count()
        refilled_cars_count = self.get_refilled_cars_count()
        file_ids = self.get_photo_file_ids()

        total_cars_count = sum(car_class_to_count.values())
        not_refilled_cars_count = total_cars_count - refilled_cars_count

        return ShiftSummary(
            staff_full_name=shift.staff.full_name,
            car_wash_name=car_wash_name,
            comfort_cars_count=car_class_to_count[CarToWash.CarType.COMFORT],
            business_cars_count=car_class_to_count[CarToWash.CarType.BUSINESS],
            vans_count=car_class_to_count[CarToWash.CarType.VAN],
            planned_cars_count=wash_type_to_count[CarToWash.WashType.PLANNED],
            urgent_cars_count=wash_type_to_count[CarToWash.WashType.URGENT],
            dry_cleaning_count=dry_cleaning_items_count,
            total_cars_count=total_cars_count,
            refilled_cars_count=refilled_cars_count,
            not_refilled_cars_count=not_refilled_cars_count,
            finish_photo_file_ids=file_ids,
        )


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
            shift_summary: ShiftSummary,
    ) -> ShiftFinishResult:
        return ShiftFinishResult(
            shift_id=self.__shift.id,
            is_first_shift=is_first_shift,
            staff_full_name=self.__shift.staff.full_name,
            car_numbers=tuple(car_numbers),
            car_wash_name=shift_summary.car_wash_name,
            comfort_cars_count=shift_summary.comfort_cars_count,
            business_cars_count=shift_summary.business_cars_count,
            vans_count=shift_summary.vans_count,
            planned_cars_count=shift_summary.planned_cars_count,
            urgent_cars_count=shift_summary.urgent_cars_count,
            dry_cleaning_count=shift_summary.dry_cleaning_count,
            total_cars_count=shift_summary.total_cars_count,
            refilled_cars_count=shift_summary.refilled_cars_count,
            not_refilled_cars_count=shift_summary.not_refilled_cars_count,
            finish_photo_file_ids=shift_summary.finish_photo_file_ids,
        )

    @transaction.atomic
    def finish_shift(self) -> ShiftFinishResult:
        is_first_shift = not has_any_finished_shift(self.__shift.staff_id)
        self.save_shift_finish_date()
        self.delete_shift_finish_photos()
        self.create_shift_finish_photos()
        car_numbers = self.get_car_numbers()

        shift_summary_interactor = ShiftSummaryInteractor(self.__shift.id)
        shift_summary = shift_summary_interactor.get_shift_summary()

        return self.create_result(
            is_first_shift=is_first_shift,
            car_numbers=car_numbers,
            shift_summary=shift_summary,
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
