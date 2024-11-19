from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.db.models import Prefetch

from car_washes.exceptions import CarWashNotFoundError
from car_washes.models import CarWash, CarWashService, CarWashServicePrice

__all__ = (
    'CarWashDetailDTO',
    'CarWashServiceDTO',
    'CarWashListItemDTO',
    'get_car_washes',
    'get_car_wash_by_id',
    'CarWashCreateResultDTO',
    'serialize_car_wash_service',
    'get_root_car_wash_services',
)


@dataclass(frozen=True, slots=True)
class CarWashCreateResultDTO:
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class CarWashListItemDTO:
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class CarWashServiceDTO:
    id: int
    name: str
    price: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class CarWashDetailDTO:
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    services: list[CarWashServiceDTO]


def get_car_washes() -> list[CarWashListItemDTO]:
    car_washes = (
        CarWash.objects
        .order_by('name')
        .values('id', 'name', 'created_at', 'updated_at')
    )
    return [
        CarWashListItemDTO(
            id=car_wash['id'],
            name=car_wash['name'],
            created_at=car_wash['created_at'],
            updated_at=car_wash['updated_at'],
        )
        for car_wash in car_washes
    ]


def get_car_wash_by_id(car_wash_id: int) -> CarWashDetailDTO:
    car_wash = (
        CarWash.objects
        .filter(id=car_wash_id)
        .prefetch_related('carwashservice_set')
        .first()
    )

    if car_wash is None:
        raise CarWashNotFoundError

    services = [
        CarWashServiceDTO(
            id=service.id,
            name=service.name,
            price=service.price,
            created_at=service.created_at,
            updated_at=service.updated_at
        )
        for service in car_wash.carwashservice_set.all()
    ]

    return CarWashDetailDTO(
        id=car_wash.id,
        name=car_wash.name,
        created_at=car_wash.created_at,
        updated_at=car_wash.updated_at,
        services=services
    )


def serialize_car_wash_service(service: CarWashService) -> dict[str, Any]:
    """Recursively serialize a CarWashService with optimized child querying."""
    if not (
            hasattr(service, 'prefetched_children')
            and service.prefetched_children
    ):
        return {
            'id': str(service.id),
            'name': service.name,
            'is_countable': service.is_countable,
        }
    return {
        'id': str(service.id),
        'name': service.name,
        'children': [
            serialize_car_wash_service(child)
            for child in service.prefetched_children
        ]
    }


def get_root_car_wash_services(
        *,
        car_wash_id: int,
        depth: int,
) -> list[dict[str, Any]]:
    """
    Retrieve root services with fully optimized nested querying.
    Minimizes database hits through select_related and prefetch_related.

    Keyword Args:
        depth (int): The depth of nested services to query.
    """
    service_ids = (
        CarWashServicePrice.objects
        # .filter(car_wash_id=car_wash_id)
        .values_list('service_id', flat=True)
    )
    print(service_ids, car_wash_id)

    prefetch = 'children'
    for _ in range(depth):
        prefetch = Prefetch(
            'children',
            queryset=CarWashService.objects.prefetch_related(prefetch),
            to_attr='prefetched_children',
        )

    root_services = (
        CarWashService.objects
        .filter(id__in=service_ids, parent__isnull=True)
        .prefetch_related(prefetch)
    )

    return [
        serialize_car_wash_service(service)
        for service in root_services
    ]
