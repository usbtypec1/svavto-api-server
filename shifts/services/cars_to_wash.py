import datetime
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone

from car_washes.models import CarWash, CarWashServicePrice
from economics.selectors import compute_car_transfer_price
from shifts.exceptions import (
    AdditionalServiceCouldNotBeProvidedError,
    CarAlreadyWashedOnShiftError,
    CarWashSameAsCurrentError,
)
from shifts.models import CarToWash, CarToWashAdditionalService, Shift


@dataclass(frozen=True, slots=True)
class CarToWashAdditionalServiceCreateResultDTO:
    id: UUID
    count: int


@dataclass(frozen=True, slots=True)
class CarToWashCreateResultDTO:
    id: int
    shift_id: int
    number: str
    class_type: str
    wash_type: str
    windshield_washer_refilled_bottle_percentage: int
    car_wash_id: int
    additional_services: list[CarToWashAdditionalServiceCreateResultDTO]


error_messages_and_exceptions = (
    (
        'Car to wash with this Number and Shift already exists.',
        CarAlreadyWashedOnShiftError,
    ),
)


def map_create_result_to_dto(
        car_to_wash: CarToWash,
        additional_services: Iterable[CarToWashAdditionalService],
) -> CarToWashCreateResultDTO:
    additional_services_dto = [
        CarToWashAdditionalServiceCreateResultDTO(
            id=service.service_id,
            count=service.count,
        )
        for service in additional_services
    ]
    return CarToWashCreateResultDTO(
        id=car_to_wash.id,
        shift_id=car_to_wash.shift_id,
        number=car_to_wash.number,
        class_type=car_to_wash.car_class,
        wash_type=car_to_wash.wash_type,
        windshield_washer_refilled_bottle_percentage=(
            car_to_wash.windshield_washer_refilled_bottle_percentage
        ),
        car_wash_id=car_to_wash.car_wash_id,
        additional_services=additional_services_dto,
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
    ).values('service_id', 'price')

    service_ids_with_prices: set[UUID] = {
        service_price['service_id']
        for service_price in car_wash_service_prices
    }

    service_ids_unable_to_provide = (
            service_ids_to_retrieve - service_ids_with_prices
    )

    if service_ids_unable_to_provide:
        raise AdditionalServiceCouldNotBeProvidedError(
            service_ids=service_ids_unable_to_provide,
        )

    return {
        service_price['service_id']: service_price['price']
        for service_price in car_wash_service_prices
    }


@transaction.atomic
def create_car_to_wash(
        *,
        shift: Shift,
        number: str,
        car_class: str,
        wash_type: str,
        windshield_washer_refilled_bottle_percentage: int,
        additional_services: list[dict],
):
    transfer_price = compute_car_transfer_price(
        class_type=car_class,
        wash_type=wash_type,
        is_extra_shift=shift.is_extra,
    )
    car_wash: CarWash = shift.car_wash
    car_to_wash = CarToWash(
        shift_id=shift.id,
        number=number,
        car_class=car_class,
        wash_type=wash_type,
        windshield_washer_refilled_bottle_percentage=(
            windshield_washer_refilled_bottle_percentage
        ),
        transfer_price=transfer_price,
        car_wash=shift.car_wash,
        comfort_class_car_washing_price=car_wash
        .comfort_class_car_washing_price,
        business_class_car_washing_price=car_wash
        .business_class_car_washing_price,
        van_washing_price=car_wash.van_washing_price,
        windshield_washer_price_per_bottle=car_wash
        .windshield_washer_price_per_bottle,
        created_at=timezone.now(),
    )
    try:
        car_to_wash.full_clean()
        car_to_wash.save()
    except ValidationError as error:
        if (
                'Добавленное авто с такими значениями полей'
                in error.messages
        ):
            raise CarAlreadyWashedOnShiftError
        raise

    additional_services = CarTransferUpdateInteractor(
        car_id=car_to_wash.id,
        windshield_washer_refilled_bottle_percentage=(
            windshield_washer_refilled_bottle_percentage
        ),
        additional_services=additional_services,
    ).execute()

    return map_create_result_to_dto(car_to_wash, additional_services)


@dataclass(frozen=True, slots=True, kw_only=True)
class CarTransferUpdateInteractor:
    """
    Args:
        car_id: The ID of the car to wash
        additional_services: List of dictionaries containing additional
        services

    """
    car_id: int
    windshield_washer_refilled_bottle_percentage: int
    additional_services: list[dict]

    @transaction.atomic
    def execute(self):
        """
        Update additional services for a car to wash.

        Raises:
            AdditionalServiceCouldNotBeProvidedError:
                If the car wash does not provide all needed services.
        """
        car_wash = (
            CarToWash.objects
            .filter(id=self.car_id)
            .values('car_wash_id').first()
        )
        car_wash_id = car_wash['car_wash_id']

        service_ids: list[UUID] = [
            service['id'] for service in
            self.additional_services
        ]

        service_id_to_price = get_car_wash_service_prices(
            car_wash_id=car_wash_id,
            car_wash_service_ids=service_ids,
        )

        CarToWash.objects.filter(id=self.car_id).update(
            windshield_washer_refilled_bottle_percentage=(
                self.windshield_washer_refilled_bottle_percentage
            ),
        )
        services = [
            CarToWashAdditionalService(
                car_id=self.car_id,
                service_id=service['id'],
                count=service['count'],
                price=service_id_to_price[service['id']],
            )
            for service in self.additional_services
        ]
        CarToWashAdditionalService.objects.filter(car_id=self.car_id).delete()
        return CarToWashAdditionalService.objects.bulk_create(services)


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
        CarToWash.objects
        .filter(shift__date=date, shift__finished_at__isnull=True)
        .values('shift__staff_id', 'shift__staff__full_name')
        .annotate(cars_count=Count('id'))
        .order_by('-cars_count')
    )
    completed_shifts_cars_count = (
        CarToWash.objects
        .filter(shift__date=date, shift__finished_at__isnull=False)
        .values('shift__staff_id', 'shift__staff__full_name')
        .annotate(cars_count=Count('id'))
        .order_by('-cars_count')
    )
    active_shifts = [
        {
            'staff_id': staff['shift__staff_id'],
            'staff_full_name': staff['shift__staff__full_name'],
            'cars_count': staff['cars_count'],
        }
        for staff in active_shifts_cars_count
    ]
    completed_shifts = [
        {
            'staff_id': staff['shift__staff_id'],
            'staff_full_name': staff['shift__staff__full_name'],
            'cars_count': staff['cars_count'],
        }
        for staff in completed_shifts_cars_count
    ]
    return {
        'date': date,
        'active_shifts': active_shifts,
        'completed_shifts': completed_shifts
    }


def get_cars_without_windshield_washer_by_date(
        date: datetime.date,
) -> list[str]:
    cars_to_wash = CarToWash.objects.filter(
        shift__date=date,
        windshield_washer_refilled_bottle_percentage=0,
    )
    cars_numbers = cars_to_wash.values_list('number', flat=True)
    return list(cars_numbers)


def update_shift_car_wash(
        *,
        shift: Shift,
        car_wash_id: int,
) -> None:
    if shift.car_wash_id == car_wash_id:
        raise CarWashSameAsCurrentError
    shift.car_wash_id = car_wash_id
    shift.save(update_fields=['car_wash_id'])


TRUNK_VACUUM_SERVICE_ID: Final[UUID] = UUID(
    '8d263cb9-f11c-456e-b055-ee89655682f1'
)


def compute_trunk_vacuum_count(
        *,
        car_wash_id: int,
        shift_id: int,
) -> int:
    result = (
        CarToWashAdditionalService.objects
        .filter(
            car__car_wash_id=car_wash_id,
            car__shift_id=shift_id,
            service_id=TRUNK_VACUUM_SERVICE_ID,
        )
        .aggregate(count=Sum('count'))
    )
    return result['count'] or 0


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
