import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from car_washes.tests.factories import CarWashFactory
from economics.models import (
    CarWashPenalty,
    CarWashSurcharge,
    CarTransporterPenalty,
    CarTransporterSurcharge,
)
from staff.tests.factories import StaffFactory

__all__ = (
    "PenaltyFactory",
    "SurchargeFactory",
    "CarWashSurchargeFactory",
    "CarWashPenaltyFactory",
)


class PenaltyFactory(DjangoModelFactory):
    class Meta:
        model = CarTransporterPenalty

    staff = factory.SubFactory(StaffFactory)
    reason = factory.Faker("sentence")
    created_at = factory.Faker("date_time")


class SurchargeFactory(DjangoModelFactory):
    class Meta:
        model = CarTransporterSurcharge

    staff = factory.SubFactory(StaffFactory)
    reason = factory.Faker("sentence")
    amount = factory.Faker("random_int", min=100, max=10000)
    created_at = factory.Faker("date_time")


class CarWashPenaltyFactory(DjangoModelFactory):
    class Meta:
        model = CarWashPenalty

    car_wash = factory.SubFactory(CarWashFactory)
    reason = factory.Faker("sentence")
    amount = factory.Faker("random_int", min=100, max=10000)
    date = factory.Faker("date_object")
    created_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )


class CarWashSurchargeFactory(DjangoModelFactory):
    class Meta:
        model = CarWashSurcharge

    car_wash = factory.SubFactory(CarWashFactory)
    reason = factory.Faker("sentence")
    amount = factory.Faker("random_int", min=100, max=10000)
    date = factory.Faker("date_object")
    created_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )
