import datetime
import math
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from shifts.exceptions import (
    CarToWashNotFoundError, ShiftNotFoundError,
    StaffHasNoActiveShiftError,
)
from shifts.models import CarToWash, CarToWashAdditionalService, Shift

__all__ = (
    'get_staff_ids_by_shift_date',
    'get_staff_ids_by_shift_ids',
    'get_shift_by_id',
    'get_staff_current_shift',
    'has_any_finished_shift',
    'CarToWashDTO',
    'get_cars_to_wash_for_period',
    'map_car_to_wash',
    'CarToWashAdditionalServiceDTO',
    'get_staff_id_by_car_id',
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
        return Shift.objects.select_related('staff', 'car_wash').get(
            id=shift_id
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
    shifts = Shift.objects.filter(id__in=shift_ids).values('id', 'staff_id')
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
        staff_id=staff_id, finished_at__isnull=False
    ).exists()


@dataclass(frozen=True, slots=True)
class CarToWashAdditionalServiceDTO:
    id: UUID
    name: str
    count: int
    total_price: int
    car_to_wash_id: int


@dataclass(frozen=True, slots=True)
class CarToWashDTO:
    id: int
    car_class: str
    shift_date: datetime.date
    washing_price: int
    windshield_washer_price: int
    windshield_washer_refilled_bottle_count: int
    additional_services: list[CarToWashAdditionalServiceDTO]


def compute_windshield_washer_refilled_bottles_count(
        windshield_washer_refilled_bottle_percentage: int,
) -> int:
    return math.ceil(windshield_washer_refilled_bottle_percentage / 100)


def group_additional_services_by_car_to_wash_id(
        additional_services: Iterable[CarToWashAdditionalServiceDTO],
) -> dict[int, list[CarToWashAdditionalServiceDTO]]:
    car_id_to_additional_services = defaultdict(list)

    for additional_service in additional_services:
        car_id = additional_service.car_to_wash_id
        car_id_to_additional_services[car_id].append(additional_service)

    return dict(car_id_to_additional_services)


def map_car_to_wash(
        cars_to_wash: Iterable[CarToWash],
        additional_services: Iterable[CarToWashAdditionalServiceDTO],
) -> list[CarToWashDTO]:
    car_id_to_additional_services = group_additional_services_by_car_to_wash_id(
        additional_services=additional_services,
    )

    mapped_cars_to_wash: list[CarToWashDTO] = []

    for car_to_wash in cars_to_wash:
        car_to_wash_additional_services = car_id_to_additional_services.get(
            car_to_wash.id,
            []
        )

        bottle_count = compute_windshield_washer_refilled_bottles_count(
            car_to_wash.windshield_washer_refilled_bottle_percentage,
        )
        mapped_cars_to_wash.append(
            CarToWashDTO(
                id=car_to_wash.id,
                car_class=car_to_wash.car_class,
                shift_date=car_to_wash.shift.date,
                washing_price=car_to_wash.washing_price,
                windshield_washer_price=car_to_wash.windshield_washer_price,
                windshield_washer_refilled_bottle_count=bottle_count,
                additional_services=car_to_wash_additional_services,
            ),
        )

    return mapped_cars_to_wash


def compute_additional_service_total_price_for_car_washes(
        *,
        count: int,
        price: int,
) -> int:
    return count * price


def map_additional_services(
        additional_services: Iterable[dict],
) -> list[CarToWashAdditionalServiceDTO]:
    return [
        CarToWashAdditionalServiceDTO(
            id=additional_service['service_id'],
            name=additional_service['service__name'],
            count=additional_service['count'],
            total_price=compute_additional_service_total_price_for_car_washes(
                count=additional_service['count'],
                price=additional_service['price'],
            ),
            car_to_wash_id=additional_service['car_id'],
        )
        for additional_service in additional_services
    ]


def get_cars_to_wash_for_period(
        *,
        car_wash_ids: Iterable[int],
        from_date: datetime.date,
        to_date: datetime.date,
) -> list[CarToWashDTO]:
    """
    Iterate through car wash records for specified car washes and date range.

    Args:
        car_wash_ids: List of car wash IDs to filter
        from_date: Start date of the period (inclusive)
        to_date: End date of the period (inclusive)

    Yields:
        Tuples of CarToWashDTO objects

    Raises:
        ValueError: If input dates are invalid or car_wash_ids is empty
    """
    if not car_wash_ids:
        raise ValueError("car_wash_ids must not be empty")

    if from_date > to_date:
        raise ValueError("from_date must be less than or equal to to_date")

    cars_to_wash = (
        CarToWash.objects
        .select_related('shift')
        .filter(
            shift__date__range=(from_date, to_date),
            car_wash_id__in=car_wash_ids,
        )
        .only(
            'id',
            'car_wash_id',
            'car_class',
            'shift__date',
            'windshield_washer_refilled_bottle_percentage',
        )
    )

    additional_services = (
        CarToWashAdditionalService.objects
        .select_related('service')
        .filter(
            car__shift__date__range=(from_date, to_date),
            car__car_wash_id__in=car_wash_ids,
        )
        .values(
            'service_id',
            'service__name',
            'count',
            'price',
            'car_id',
        )
    )
    additional_services = map_additional_services(additional_services)

    return map_car_to_wash(
        cars_to_wash=cars_to_wash,
        additional_services=additional_services,
    )


def get_staff_id_by_car_id(car_id: int) -> int:
    try:
        car = CarToWash.objects.select_related('shift').get(id=car_id)
    except CarToWash.DoesNotExist:
        raise CarToWashNotFoundError
    return car.shift.staff_id
