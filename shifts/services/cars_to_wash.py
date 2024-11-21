import datetime
from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count

from car_washes.models import CarWashServicePrice
from shifts.exceptions import (
    AdditionalServiceCouldNotBeProvidedError, CarAlreadyWashedOnShiftError,
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


def validate_car_wash_provides_services(
        *,
        car_wash_id: int,
        service_ids: Iterable[UUID],
) -> None:
    """
    Validate that the car wash provides all needed services.

    Keyword Args:
        car_wash_id: The ID of the car wash.
        service_ids: List of service IDs to provide.

    Raises:
        AdditionalServiceCouldNotBeProvidedError:
            If the car wash does not provide all needed services.
    """
    service_ids_to_provide = set(service_ids)

    service_ids_available_in_car_wash: set[UUID] = set(
        CarWashServicePrice.objects
        .filter(car_wash_id=car_wash_id, service_id__in=service_ids_to_provide)
        .values_list('service_id', flat=True)
    )

    service_ids_unable_to_provide = (
            service_ids_to_provide - service_ids_available_in_car_wash
    )

    if service_ids_unable_to_provide:
        raise AdditionalServiceCouldNotBeProvidedError(
            service_ids=service_ids_unable_to_provide,
        )


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
    car_to_wash = CarToWash(
        shift_id=shift.id,
        number=number,
        car_class=car_class,
        wash_type=wash_type,
        windshield_washer_refilled_bottle_percentage=(
            windshield_washer_refilled_bottle_percentage
        ),
        car_wash_id=shift.car_wash_id,
    )
    try:
        car_to_wash.full_clean()
        car_to_wash.save()
    except ValidationError as error:
        if ('Car to wash with this Number and Shift already exists.' in
                error.messages):
            raise CarAlreadyWashedOnShiftError
        raise

    additional_services = update_car_to_wash_additional_services(
        car_id=car_to_wash.id,
        additional_services=additional_services,
    )

    return map_create_result_to_dto(car_to_wash, additional_services)


@transaction.atomic
def update_car_to_wash_additional_services(
        *,
        car_id: int,
        additional_services: list[dict],
) -> list[CarToWashAdditionalService]:
    """
    Update additional services for a car to wash.

    Keyword Args:
        car_id: The ID of the car to wash
        additional_services: List of dictionaries containing additional services

    Raises:
        AdditionalServiceCouldNotBeProvidedError:
            If the car wash does not provide all needed services.
    """
    car_wash = CarToWash.objects.filter(id=car_id).values('car_wash_id').first()
    car_wash_id = car_wash['car_wash_id']

    service_ids = [UUID(service['id']) for service in additional_services]
    validate_car_wash_provides_services(
        car_wash_id=car_wash_id, service_ids=service_ids
    )
    services = [
        CarToWashAdditionalService(
            car_id=car_id,
            service_id=service['id'],
            count=service['count'],
        )
        for service in additional_services
    ]
    CarToWashAdditionalService.objects.filter(car_id=car_id).delete()
    return CarToWashAdditionalService.objects.bulk_create(services)


def get_staff_cars_count_by_date(date: datetime.date) -> list[dict]:
    """
    Compute the count of cars assigned to each staff member for a specific date.

    Args:
        date (date): The date to count cars for

    Returns:
        List[Dict]: List of dictionaries containing staff information and
        their car count
        Example: [
            {
                'staff_id': 1,
                'staff_full_name': 'John Doe',
                'cars_count': 5
            },
            ...
        ]
    """
    shifts = (
        Shift.objects
        .select_related('staff')
        .filter(
            date=date,
            finished_at__isnull=True,
        )
        .annotate(cars_count=Count('id'))
        .values('staff_id', 'staff__full_name', 'cars_count')
        .order_by('-cars_count')
    )
    return [
        {
            'staff_id': shift['staff_id'],
            'staff_full_name': shift['staff__full_name'],
            'cars_count': shift['cars_count'],
        }
        for shift in shifts
    ]


def get_cars_without_windshield_washer_by_date(
        date: datetime.date,
) -> list[str]:
    return CarToWash.objects.filter(
        shift__date=date,
        windshield_washer_refilled_bottle_percentage=0,
    ).values_list('number', flat=True)


def update_shift_car_wash(
        *,
        shift: Shift,
        car_wash_id: int,
) -> None:
    if shift.car_wash_id == car_wash_id:
        raise CarWashSameAsCurrentError
    shift.car_wash_id = car_wash_id
    shift.save(update_fields=['car_wash_id'])
