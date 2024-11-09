from dataclasses import dataclass
from datetime import datetime

from car_washes.exceptions import CarWashNotFoundError
from car_washes.models import CarWash

__all__ = (
    'CarWashDetailDTO',
    'CarWashServiceDTO',
    'CarWashListItemDTO',
    'get_car_washes',
    'get_car_wash_by_id',
    'CarWashCreateResultDTO',
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
