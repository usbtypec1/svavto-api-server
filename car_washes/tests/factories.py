import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from car_washes.models import CarWash

__all__ = ("CarWashFactory",)


class CarWashFactory(DjangoModelFactory):
    class Meta:
        model = CarWash

    name = factory.Faker("address")
    comfort_class_car_washing_price = factory.Faker(
        "random_int",
        min=100,
        max=10000,
    )
    business_class_car_washing_price = factory.Faker(
        "random_int",
        min=100,
        max=10000,
    )
    van_washing_price = factory.Faker(
        "random_int",
        min=100,
        max=10000,
    )
    windshield_washer_price_per_bottle = factory.Faker(
        "random_int",
        min=100,
        max=10000,
    )
    created_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )
    updated_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )
