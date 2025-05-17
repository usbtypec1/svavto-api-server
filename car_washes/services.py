from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from car_washes.exceptions import (
    CarWashAlreadyExistsError,
    CarWashNotFoundError,
)
from car_washes.models import CarWash


def create_car_wash(
        *,
        name: str,
        car_transporters_comfort_class_car_washing_price: int,
        car_transporters_business_class_car_washing_price: int,
        car_transporters_van_washing_price: int,
        car_transporters_and_washers_comfort_class_price: int,
        car_transporters_and_washers_business_class_price: int,
        car_transporters_and_washers_van_price: int,
        windshield_washer_price_per_bottle: int,
        is_hidden: bool,
) -> CarWash:
    car_wash = CarWash(
        name=name,
        comfort_class_car_washing_price=(
            car_transporters_comfort_class_car_washing_price
        ),
        business_class_car_washing_price=(
            car_transporters_business_class_car_washing_price
        ),
        van_washing_price=(
            car_transporters_van_washing_price
        ),
        windshield_washer_price_per_bottle=windshield_washer_price_per_bottle,
        car_transporters_and_washers_comfort_class_price=(
            car_transporters_and_washers_comfort_class_price
        ),
        car_transporters_and_washers_business_class_price=(
            car_transporters_and_washers_business_class_price
        ),
        car_transporters_and_washers_van_price=(
            car_transporters_and_washers_van_price
        ),
        is_hidden=is_hidden,
    )

    try:
        car_wash.full_clean()
        car_wash.save()
    except (ValidationError, IntegrityError) as error:
        if 'unique_car_wash_name' in str(error):
            raise CarWashAlreadyExistsError
        raise
    return car_wash


def update_car_wash(
        *,
        car_wash: CarWash,
        name: str,
        comfort_class_car_washing_price: int,
        business_class_car_washing_price: int,
        van_washing_price: int,
        windshield_washer_price_per_bottle: int,
        is_hidden: bool,
) -> CarWash:
    car_wash.name = name
    car_wash.comfort_class_car_washing_price = comfort_class_car_washing_price
    car_wash.business_class_car_washing_price = (
        business_class_car_washing_price)
    car_wash.van_washing_price = van_washing_price
    car_wash.windshield_washer_price_per_bottle = (
        windshield_washer_price_per_bottle)
    car_wash.is_hidden = is_hidden

    try:
        car_wash.full_clean()
    except ValidationError as error:
        if "Car wash with this Name already exists." in error.messages:
            raise CarWashAlreadyExistsError
        raise

    car_wash.save(
        update_fields=(
            "name",
            "comfort_class_car_washing_price",
            "business_class_car_washing_price",
            "van_washing_price",
            "windshield_washer_price_per_bottle",
            "is_hidden",
            "updated_at",
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
