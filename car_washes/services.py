from django.core.exceptions import ValidationError
from django.db import IntegrityError

from car_washes.exceptions import (
    CarWashAlreadyExistsError,
    CarWashNotFoundError,
)
from car_washes.models import CarWash
from car_washes.selectors import CarWashCreateResultDTO

__all__ = (
    'create_car_wash',
    'update_car_wash',
    'delete_car_wash',
    'ensure_car_wash_exists',
)


def create_car_wash(*, name: str) -> CarWashCreateResultDTO:
    car_wash = CarWash(name=name)
    try:
        car_wash.full_clean()
    except ValidationError as error:
        if 'Car wash with this Name already exists.' in error.messages:
            raise CarWashAlreadyExistsError
        raise
    car_wash.save()
    return CarWashCreateResultDTO(
        id=car_wash.id,
        name=car_wash.name,
        created_at=car_wash.created_at,
        updated_at=car_wash.updated_at,
    )


def update_car_wash(*, car_wash_id: int, name: str) -> None:
    updated_count = CarWash.objects.filter(id=car_wash_id).update(name=name)
    if updated_count == 0:
        raise CarWashNotFoundError


def delete_car_wash(*, car_wash_id: int) -> None:
    deleted_count, _ = CarWash.objects.filter(id=car_wash_id).delete()
    if deleted_count == 0:
        raise CarWashNotFoundError


def ensure_car_wash_exists(car_wash_id: int) -> None:
    if not CarWash.objects.filter(id=car_wash_id).exists():
        raise CarWashNotFoundError
