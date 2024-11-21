from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

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
    'ensure_service_exists',
    'ensure_car_wash_exists',
    'get_all_flatten_car_wash_services',
    'get_flatten_specific_car_wash_services',
)

from shifts.models import CarToWash


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


def get_car_wash_by_id(car_wash_id: int) -> CarWash:
    try:
        return CarWash.objects.get(id=car_wash_id)
    except CarWash.DoesNotExist:
        raise CarWashNotFoundError


def get_all_flatten_car_wash_services() -> list[dict]:
    car_wash_services = CarWashService.objects.values(
        'id',
        'name',
        'is_countable',
        'parent__id',
        'parent__name',
    )
    parent_ids = {
        service['parent__id'] for service in car_wash_services
        if service['parent__id']
    }
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
        if service['id'] not in parent_ids
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
        .order_by('parent')
    )
    parent_ids = set(CarWashService.objects.values_list('parent_id', flat=True))
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
        if service['id'] not in parent_ids
    ]


def ensure_car_wash_exists(car_wash_id: int) -> None:
    if not CarWash.objects.filter(id=car_wash_id).exists():
        raise CarWashNotFoundError


def ensure_service_exists(service_id: UUID) -> None:
    if not CarWashService.objects.filter(id=service_id).exists():
        raise CarWashServiceNotFoundError
