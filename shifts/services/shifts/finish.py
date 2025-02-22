import collections
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from car_washes.models import CarWash
from shifts.models import CarToWash, Shift, ShiftFinishPhoto
from shifts.selectors import has_any_finished_shift
from shifts.services.cars_to_wash import (
    compute_dry_cleaning_items_count,
    compute_trunk_vacuum_count,
)


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
    trunk_vacuum_count: int


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
            trunk_vacuum_count = compute_trunk_vacuum_count(
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
                urgent_cars_count=wash_type_to_count[
                    CarToWash.WashType.URGENT],
                dry_cleaning_count=dry_cleaning_items_count,
                total_cars_count=total_cars_count,
                refilled_cars_count=refilled_cars_count,
                not_refilled_cars_count=not_refilled_cars_count,
                trunk_vacuum_count=trunk_vacuum_count,
            )
            car_washes_summaries.append(car_wash_transferred_cars_summary)

        return ShiftSummary(
            staff_id=shift.staff.id,
            staff_full_name=shift.staff.full_name,
            shift_id=shift.id,
            car_washes=car_washes_summaries,
        )
