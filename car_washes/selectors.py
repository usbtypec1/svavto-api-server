from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from django.db.models import QuerySet

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
    'ensure_service_exists',
    'ensure_car_wash_exists',
    'get_all_flatten_car_wash_services',
    'get_flatten_specific_car_wash_services',
)


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


def get_car_washes() -> QuerySet[CarWash]:
    return CarWash.objects.order_by('name')


def get_car_wash_by_id(car_wash_id: int) -> CarWash:
    try:
        return CarWash.objects.get(id=car_wash_id)
    except CarWash.DoesNotExist:
        raise CarWashNotFoundError


@dataclass(frozen=True, slots=True)
class CarWashServiceParentDTO:
    id: UUID
    name: str


@dataclass(frozen=True, slots=True)
class CarWashServiceDTO:
    id: UUID
    name: str
    is_countable: bool
    parent: CarWashServiceParentDTO | None


def get_all_flatten_car_wash_services(
        car_wash_ids: Iterable[int] | None = None,
) -> list[CarWashServiceDTO]:
    if car_wash_ids is not None:
        service_prices = (
            CarWashServicePrice.objects
            .filter(car_wash_id__in=car_wash_ids)
            .select_related('service', 'service__parent')
            .only(
                'service__id',
                'service__name',
                'service__is_countable',
                'service__parent__id',
                'service__parent__name',
                'service__priority',
            )
        )
        car_wash_services = sorted({
            service_price.service
            for service_price in service_prices
        }, key=lambda service: (not service.parent_id, service.priority), reverse=True)
    else:
        car_wash_services = (
            CarWashService.objects
            .select_related('parent')
            .only(
                'id',
                'name',
                'is_countable',
                'parent__id',
                'parent__name',
            )
            .order_by('-priority')
        )

    parent_ids: set[UUID] = {
        service.parent_id
        for service in car_wash_services
        if service.parent_id is not None
    }
    result: list[CarWashServiceDTO] = []

    for service in car_wash_services:
        if service.id in parent_ids:
            continue

        if service.parent is not None:
            parent = CarWashServiceParentDTO(
                id=service.parent.id,
                name=service.parent.name,
            )
        else:
            parent = None

        result.append(
            CarWashServiceDTO(
                id=service.id,
                name=service.name,
                is_countable=service.is_countable,
                parent=parent,
            ),
        )

    return result


def get_flatten_specific_car_wash_services(car_wash_id: int) -> list[dict]:
    service_ids_and_prices = CarWashServicePrice.objects.filter(
        car_wash_id=car_wash_id
    ).values_list('service_id', 'price')
    if not service_ids_and_prices:
        return []
    service_id_to_price = {
        service_id: price for service_id, price in service_ids_and_prices
    }
    car_wash_services = (
        CarWashService.objects.filter(id__in=service_id_to_price.keys())
        .values(
            'id',
            'name',
            'is_countable',
            'parent__id',
            'parent__name',
        )
        .order_by('parent', '-priority')
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
            }
            if service['parent__id']
            else None,
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
