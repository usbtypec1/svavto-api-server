import datetime
from typing import Final
from uuid import UUID
from collections.abc import Iterable

from django.db.models import Count, Sum

from shifts.exceptions import (
    CarAlreadyWashedOnShiftError,
    CarWashSameAsCurrentError,
)
from shifts.models import CarToWash, CarToWashAdditionalService, Shift
from car_washes.models import CarWashServicePrice
from shifts.exceptions import AdditionalServiceCouldNotBeProvidedError


error_messages_and_exceptions = (
    (
        "Car to wash with this Number and Shift already exists.",
        CarAlreadyWashedOnShiftError,
    ),
)


def get_car_wash_service_prices(
    *,
    car_wash_id: int,
    car_wash_service_ids: Iterable[UUID],
) -> dict[UUID, int]:
    """
    Get the prices for the provided car wash services in specific car wash.
    It's guaranteed that the car wash provides all services.

    Keyword Args:
        car_wash_id: The ID of the car wash.
        car_wash_service_ids: List of car wash service IDs to get prices for.

    Returns:
        Dict: Dictionary containing service IDs as keys and prices as values.

    Raises:
        AdditionalServiceCouldNotBeProvidedError:
            If the car wash does not provide all needed services.
    """
    service_ids_to_retrieve = set(car_wash_service_ids)
    car_wash_service_prices = CarWashServicePrice.objects.filter(
        car_wash_id=car_wash_id,
    ).values("service_id", "price")

    service_ids_with_prices: set[UUID] = {
        service_price["service_id"] for service_price in car_wash_service_prices
    }

    service_ids_unable_to_provide = service_ids_to_retrieve - service_ids_with_prices

    if service_ids_unable_to_provide:
        raise AdditionalServiceCouldNotBeProvidedError(
            service_ids=service_ids_unable_to_provide,
        )

    return {
        service_price["service_id"]: service_price["price"]
        for service_price in car_wash_service_prices
    }


def get_staff_cars_count_by_date(date: datetime.date) -> dict:
    """
    Compute the count of cars assigned to each staff member for a specific
    date,
    categorized by shift status.

    Args:
        date (datetime.date): The date to count cars for

    Returns:
        Dict: A dictionary containing two lists of staff car counts:
        {
            'active_shifts': [
                {
                    'staff_id': int,
                    'staff_full_name': str,
                    'cars_count': int
                }
            ],
            'completed_shifts': [
                {
                    'staff_id': int,
                    'staff_full_name': str,
                    'cars_count': int
                }
            ]
        }

    Raises:
        ValueError: If the provided date is invalid or in the future
    """
    active_shifts_cars_count = (
        CarToWash.objects.filter(shift__date=date, shift__finished_at__isnull=True)
        .values("shift__staff_id", "shift__staff__full_name")
        .annotate(cars_count=Count("id"))
        .order_by("-cars_count")
    )
    completed_shifts_cars_count = (
        CarToWash.objects.filter(shift__date=date, shift__finished_at__isnull=False)
        .values("shift__staff_id", "shift__staff__full_name")
        .annotate(cars_count=Count("id"))
        .order_by("-cars_count")
    )
    active_shifts = [
        {
            "staff_id": staff["shift__staff_id"],
            "staff_full_name": staff["shift__staff__full_name"],
            "cars_count": staff["cars_count"],
        }
        for staff in active_shifts_cars_count
    ]
    completed_shifts = [
        {
            "staff_id": staff["shift__staff_id"],
            "staff_full_name": staff["shift__staff__full_name"],
            "cars_count": staff["cars_count"],
        }
        for staff in completed_shifts_cars_count
    ]
    return {
        "date": date,
        "active_shifts": active_shifts,
        "completed_shifts": completed_shifts,
    }


def get_cars_without_windshield_washer_by_date(
    date: datetime.date,
) -> list[str]:
    cars_to_wash = CarToWash.objects.filter(
        shift__date=date,
        windshield_washer_refilled_bottle_percentage=0,
        windshield_washer_type=CarToWash.WindshieldWasherType.ANTIFREEZE,
    )
    cars_numbers = cars_to_wash.values_list("number", flat=True)
    return list(cars_numbers)


def update_shift_car_wash(
    *,
    shift: Shift,
    car_wash_id: int,
) -> None:
    if shift.car_wash_id == car_wash_id:
        raise CarWashSameAsCurrentError
    shift.car_wash_id = car_wash_id
    shift.save(update_fields=["car_wash_id"])


TRUNK_VACUUM_SERVICE_ID: Final[UUID] = UUID("8d263cb9-f11c-456e-b055-ee89655682f1")


def compute_trunk_vacuum_count(
    *,
    car_wash_id: int,
    shift_id: int,
) -> int:
    result = CarToWashAdditionalService.objects.filter(
        car__car_wash_id=car_wash_id,
        car__shift_id=shift_id,
        service_id=TRUNK_VACUUM_SERVICE_ID,
    ).aggregate(count=Sum("count"))
    return result["count"] or 0


def compute_dry_cleaning_items_count(
    *,
    car_wash_id: int,
    shift_id: int,
) -> int:
    result = CarToWashAdditionalService.objects.filter(
        car__car_wash_id=car_wash_id,
        car__shift_id=shift_id,
        service__is_dry_cleaning=True,
    ).aggregate(count=Sum("count"))
    return result["count"] or 0
