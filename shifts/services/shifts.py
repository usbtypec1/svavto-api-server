import collections
import datetime
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache

from django.db import transaction
from django.db.models import QuerySet, Sum
from django.utils import timezone

from car_washes.models import CarWash
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


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftItem:
    id: int
    date: datetime.date


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftsCreateResult:
    staff_id: int
    staff_full_name: str
    shifts: list[ShiftItem]


@dataclass(frozen=True, slots=True)
class ShiftTestCreateResult:
    staff_id: int
    staff_full_name: str
    shift_id: int
    shift_date: datetime.date


@dataclass(frozen=True, slots=True)
class ShiftExtraCreateResult:
    staff_id: int
    staff_full_name: str
    shift_id: int
    shift_date: datetime.date


def get_existing_shift_dates(
        *,
        staff_id: int,
        expected_dates: Iterable[datetime.date],
) -> set[datetime.date]:
    """
    Get existing shift dates from the database.

    Keyword Args:
        staff_id: staff id.
        expected_dates: existing shifts within these dates.

    Returns:
        set[datetime.date]: dates of existing shifts.
    """
    return set(
        Shift.objects
        .filter(
            staff_id=staff_id,
            date__in=expected_dates,
            is_test=False,
        )
        .values_list('date', flat=True)
    )


def validate_conflict_shift_dates(
        *,
        staff_id: int,
        expected_dates: Iterable[datetime.date],
) -> None:
    """
    Check if there are any conflicts with existing shifts.

    Keyword Args:
        staff_id: staff id.
        expected_dates: dates of shifts to be created.

    Raises:
        ShiftAlreadyExistsError: If shift already exists on any expected date.
    """
    existing_shift_dates = get_existing_shift_dates(
        staff_id=staff_id,
        expected_dates=expected_dates,
    )
    print(existing_shift_dates, set(expected_dates))
    conflict_dates = set(expected_dates).intersection(existing_shift_dates)
    if conflict_dates:
        raise ShiftAlreadyExistsError(conflict_dates=conflict_dates)


@transaction.atomic
def create_test_shift(
        *,
        staff: Staff,
        date: datetime.date,
) -> ShiftTestCreateResult:
    """
    Create test shift for staff for specific date or refresh test shift.

    Keyword Args:
        staff: staff ORM object.
        date: date of test shift.

    Returns:
        ShiftTestCreateResult object.
    """
    Shift.objects.filter(staff_id=staff.id, date=date).delete()
    shift = Shift(
        staff_id=staff.id,
        date=date,
        is_test=True,
    )
    shift.full_clean()
    shift.save()
    return ShiftTestCreateResult(
        staff_id=staff.id,
        staff_full_name=staff.full_name,
        shift_id=shift.id,
        shift_date=shift.date,
    )


@transaction.atomic
def create_extra_shift(
        *,
        staff: Staff,
        date: datetime.date,
) -> ShiftExtraCreateResult:
    """
    Create extra shift for staff for specific date.

    Keyword Args:
        staff: staff ORM object.
        date: date of extra shift.

    Raises:
        ShiftAlreadyExistsError: If shift already exists on the date.

    Returns:
        ShiftExtraCreateResult object.
    """
    validate_conflict_shift_dates(staff_id=staff.id, expected_dates=[date])

    shift = Shift(
        staff_id=staff.id,
        date=date,
        is_extra=True,
    )
    shift.full_clean()
    shift.save()
    return ShiftExtraCreateResult(
        staff_id=staff.id,
        staff_full_name=staff.full_name,
        shift_id=shift.id,
        shift_date=shift.date,
    )


def create_regular_shifts(
        *,
        staff: Staff,
        dates: Iterable[datetime.date],
) -> ShiftsCreateResult:
    """
    Create regular shifts for staff for specific dates.

    Keyword Args:
        staff: staff to create shifts for.
        dates: shift dates to create.

    Raises:
        ShiftAlreadyExistsError: If shift already exists on any date.

    Returns:
        ShiftsCreateResult object.
    """

    validate_conflict_shift_dates(staff_id=staff.id, expected_dates=dates)

    shifts_to_create = [Shift(staff=staff, date=date) for date in dates]
    shifts = Shift.objects.bulk_create(shifts_to_create)

    shifts = [
        ShiftItem(id=shift.id, date=shift.date)
        for shift in shifts
    ]
    return ShiftsCreateResult(
        staff_id=staff.id,
        staff_full_name=staff.full_name,
        shifts=shifts,
    )


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


def ensure_staff_has_no_active_shift(staff_id: int) -> None:
    if Shift.objects.filter(
            staff_id=staff_id,
            started_at__isnull=False,
            finished_at__isnull=True,
    ).exists():
        raise StaffHasActiveShiftError


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashTransferredCarsSummary:
    car_wash_id: int
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


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftSummary:
    staff_id: int
    staff_full_name: str
    shift_id: int
    car_washes: list[CarWashTransferredCarsSummary]


@dataclass(frozen=True, slots=True)
class ShiftFinishResult(ShiftSummary):
    is_first_shift: bool
    finish_photo_file_ids: list[str]


def compute_dry_cleaning_items_count(
        *,
        car_wash_id: int,
        shift_id: int,
) -> int:
    result = (
        CarToWashAdditionalService.objects
        .filter(
            car__car_wash_id=car_wash_id,
            car__shift_id=shift_id,
            service__is_dry_cleaning=True,
        )
        .aggregate(count=Sum('count'))
    )
    return result['count'] or 0


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

    def get_cars_to_wash(self) -> QuerySet[CarToWash]:
        return (
            CarToWash.objects
            .select_related('car_wash')
            .filter(shift=self.get_shift())
        )

    def execute(self) -> ShiftSummary:
        shift = self.get_shift()
        cars_to_wash = self.get_cars_to_wash()

        car_wash_id_to_name: dict[int, str] = {
            car_wash['id']: car_wash['name']
            for car_wash in CarWash.objects.values('id', 'name')
        }

        car_wash_id_to_cars = collections.defaultdict(list)
        for car in cars_to_wash:
            car_wash_id_to_cars[car.car_wash_id].append(car)

        car_washes_summaries: list[CarWashTransferredCarsSummary] = []

        for car_wash_id, cars in car_wash_id_to_cars.items():
            wash_type_to_count = collections.defaultdict(int)
            car_class_to_count = collections.defaultdict(int)
            refilled_cars_count = 0

            for car in cars:
                wash_type_to_count[car.wash_type] += 1
                car_class_to_count[car.car_class] += 1
                refilled_cars_count += int(
                    car.is_windshield_washer_refilled
                )

            car_wash_name = car_wash_id_to_name.get(car_wash_id, 'не выбрано')
            total_cars_count = len(cars)
            not_refilled_cars_count = total_cars_count - refilled_cars_count

            dry_cleaning_items_count = compute_dry_cleaning_items_count(
                car_wash_id=car_wash_id,
                shift_id=shift.id,
            )

            car_wash_transferred_cars_summary = CarWashTransferredCarsSummary(
                car_wash_id=car_wash_id,
                car_wash_name=car_wash_name,
                comfort_cars_count=car_class_to_count[
                    CarToWash.CarType.COMFORT],
                business_cars_count=car_class_to_count[
                    CarToWash.CarType.BUSINESS],
                vans_count=car_class_to_count[CarToWash.CarType.VAN],
                planned_cars_count=wash_type_to_count[
                    CarToWash.WashType.PLANNED],
                urgent_cars_count=wash_type_to_count[CarToWash.WashType.URGENT],
                dry_cleaning_count=dry_cleaning_items_count,
                total_cars_count=total_cars_count,
                refilled_cars_count=refilled_cars_count,
                not_refilled_cars_count=not_refilled_cars_count,
            )
            car_washes_summaries.append(car_wash_transferred_cars_summary)

        return ShiftSummary(
            staff_id=shift.staff.id,
            staff_full_name=shift.staff.full_name,
            shift_id=shift.id,
            car_washes=car_washes_summaries,
        )


class ShiftFinishInteractor:

    def __init__(
            self,
            *,
            shift: Shift,
            shift_summary: ShiftSummary,
            photo_file_ids: Iterable[str],
    ):
        self.__shift = shift
        self.__shift_summary = shift_summary
        self.__photo_file_ids = list(photo_file_ids)

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

    def create_result(
            self,
            is_first_shift: bool,
    ) -> ShiftFinishResult:
        return ShiftFinishResult(
            is_first_shift=is_first_shift,
            shift_id=self.__shift_summary.shift_id,
            staff_id=self.__shift_summary.staff_id,
            staff_full_name=self.__shift.staff.full_name,
            car_washes=self.__shift_summary.car_washes,
            finish_photo_file_ids=self.__photo_file_ids,
        )

    @transaction.atomic
    def finish_shift(self) -> ShiftFinishResult:
        is_first_shift = not has_any_finished_shift(self.__shift.staff_id)
        self.save_shift_finish_date()
        self.delete_shift_finish_photos()
        self.create_shift_finish_photos()
        return self.create_result(is_first_shift=is_first_shift)


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
