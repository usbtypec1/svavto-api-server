import factory
from django.utils import timezone
from factory.django import DjangoModelFactory
from uuid import uuid4

from car_washes.models import CarWash, CarWashService, CarWashServicePrice


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


class CarWashServiceFactory(DjangoModelFactory):
    class Meta:
        model = CarWashService

    id = factory.LazyFunction(uuid4)
    name = factory.Faker("name")
    is_countable = factory.Faker("boolean")
    parent = None
    is_dry_cleaning = factory.Faker("boolean")
    priority = factory.Faker("random_int", min=1, max=1000)
    created_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )
    updated_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )


class CarWashServicePriceFactory(DjangoModelFactory):
    class Meta:
        model = CarWashServicePrice

    car_wash = factory.SubFactory(CarWashFactory)
    service = factory.SubFactory(CarWashServiceFactory)
    price = factory.Faker("random_int", min=1, max=1000)
    created_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )
    updated_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )
