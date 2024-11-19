from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from django.db.models import Prefetch

from car_washes.exceptions import (
    CarWashNotFoundError,
    CarWashServiceNotFoundError,
)
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
    'ensure_service_exists',
    'ensure_car_wash_exists',
    'get_all_flatten_car_wash_services',
    'get_flatten_specific_car_wash_services',
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
        car_wash_id: int | None,
        depth: int,
) -> list[dict[str, Any]]:
    """
    Retrieve root services with fully optimized nested querying.
    Minimizes database hits through select_related and prefetch_related.

    Keyword Args:
        car_wash_id (int | None): The car wash ID to filter services by.
        depth (int): The depth of nested services to query.
    """
    service_ids = (
        CarWashServicePrice.objects
        .filter(car_wash_id=car_wash_id)
        .values_list('service_id', flat=True)
    )

    prefetch = 'children'
    for _ in range(depth):
        queryset = CarWashService.objects.prefetch_related(prefetch)
        if car_wash_id is not None:
            queryset = queryset.filter(id__in=service_ids)
        prefetch = Prefetch(
            'children',
            queryset=queryset,
            to_attr='prefetched_children',
        )

    root_services = (
        CarWashService.objects
        .filter(parent__isnull=True)
        .prefetch_related(prefetch)
    )
    if car_wash_id is not None:
        root_services = root_services.filter(id__in=service_ids)

    return [
        serialize_car_wash_service(service)
        for service in root_services
    ]


def get_all_flatten_car_wash_services() -> list[dict]:
    car_wash_services = CarWashService.objects.values(
        'id',
        'name',
        'is_countable',
        'parent__id',
        'parent__name',
    )
    return [
        {
            'id': str(service['id']),
            'name': service['name'],
            'is_countable': service['is_countable'],
            'parent': {
                'id': str(service['parent__id']),
                'name': service['parent__name'],
            } if service['parent__id'] else None
        }
        for service in car_wash_services
    ]


def get_flatten_specific_car_wash_services(car_wash_id: int) -> list[dict]:
    service_ids_and_prices = (
        CarWashServicePrice.objects
        .filter(car_wash_id=car_wash_id)
        .values_list('service_id', 'price')
    )
    if not service_ids_and_prices:
        return []
    service_id_to_price = {
        service_id: price
        for service_id, price in service_ids_and_prices
    }
    car_wash_services = (
        CarWashService.objects
        .filter(id__in=service_id_to_price.keys())
        .values(
            'id',
            'name',
            'is_countable',
            'parent__id',
            'parent__name',
        )
    )
    return [
        {
            'id': str(service['id']),
            'name': service['name'],
            'is_countable': service['is_countable'],
            'price': service_id_to_price[service['id']],
            'parent': {
                'id': str(service['parent__id']),
                'name': service['parent__name'],
            } if service['parent__id'] else None
        }
        for service in car_wash_services
    ]


def ensure_car_wash_exists(car_wash_id: int) -> None:
    if not CarWash.objects.filter(id=car_wash_id).exists():
        raise CarWashNotFoundError


def ensure_service_exists(service_id: UUID) -> None:
    if not CarWashService.objects.filter(id=service_id).exists():
        raise CarWashServiceNotFoundError
