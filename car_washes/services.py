from django.core.exceptions import ValidationError

from car_washes.exceptions import (
    CarWashAlreadyExistsError,
    CarWashNotFoundError,
)
from car_washes.models import CarWash

__all__ = (
    'create_car_wash',
    'update_car_wash',
    'delete_car_wash',
    'ensure_car_wash_exists',
)


def create_car_wash(
        *,
        name: str,
        comfort_class_car_transfer_price: int,
        business_class_car_transfer_price: int,
        van_transfer_price: int,
        windshield_washer_price_per_bottle: int,
) -> CarWash:
    car_wash = CarWash(
        name=name,
        comfort_class_car_transfer_price=comfort_class_car_transfer_price,
        business_class_car_transfer_price=business_class_car_transfer_price,
        van_transfer_price=van_transfer_price,
        windshield_washer_price_per_bottle=windshield_washer_price_per_bottle,
    )

    try:
        car_wash.full_clean()
    except ValidationError as error:
        if 'Car wash with this Name already exists.' in error.messages:
            raise CarWashAlreadyExistsError
        raise

    car_wash.save()
    return car_wash


def update_car_wash(
        *,
        car_wash: CarWash,
        name: str,
        comfort_class_car_transfer_price: int,
        business_class_car_transfer_price: int,
        van_transfer_price: int,
        windshield_washer_price_per_bottle: int,
) -> CarWash:
    car_wash.name = name
    car_wash.comfort_class_car_transfer_price = comfort_class_car_transfer_price
    car_wash.business_class_car_transfer_price = (
        business_class_car_transfer_price
    )
    car_wash.van_transfer_price = van_transfer_price
    car_wash.windshield_washer_price_per_bottle = windshield_washer_price_per_bottle

    try:
        car_wash.full_clean()
    except ValidationError as error:
        if 'Car wash with this Name already exists.' in error.messages:
            raise CarWashAlreadyExistsError
        raise

    car_wash.save(
        update_fields=(
            'name',
            'comfort_class_car_transfer_price',
            'business_class_car_transfer_price',
            'van_transfer_price',
            'windshield_washer_price_per_bottle',
            'updated_at',
        ),
    )
    return car_wash


def delete_car_wash(*, car_wash_id: int) -> None:
    deleted_count, _ = CarWash.objects.filter(id=car_wash_id).delete()
    if deleted_count == 0:
        raise CarWashNotFoundError


def ensure_car_wash_exists(car_wash_id: int) -> None:
    if not CarWash.objects.filter(id=car_wash_id).exists():
        raise CarWashNotFoundError
