from dataclasses import dataclass
from datetime import datetime

from car_washes.exceptions import CarWashNotFoundError
from car_washes.models import CarWash

__all__ = ('CarWashDTO', 'get_car_washes', 'get_car_wash_by_id')


@dataclass(frozen=True, slots=True)
class CarWashDTO:
    id: int
    name: str
    created_at: datetime
    updated_at: datetime


def get_car_washes() -> list[CarWashDTO]:
    car_washes = (
        CarWash.objects
        .order_by('name')
        .values('id', 'name', 'created_at', 'updated_at')
    )
    return [
        CarWashDTO(
            id=car_wash['id'],
            name=car_wash['name'],
            created_at=car_wash['created_at'],
            updated_at=car_wash['updated_at'],
        )
        for car_wash in car_washes
    ]


def get_car_wash_by_id(car_wash_id: int) -> CarWashDTO:
    car_wash = (
        CarWash.objects
        .filter(id=car_wash_id)
        .values('id', 'name', 'created_at', 'updated_at')
        .first()
    )
    if car_wash is None:
        raise CarWashNotFoundError
    return CarWashDTO(
        id=car_wash['id'],
        name=car_wash['name'],
        created_at=car_wash['created_at'],
        updated_at=car_wash['updated_at'],
    )
