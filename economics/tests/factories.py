import factory
from factory.django import DjangoModelFactory

from economics.models import Penalty, Surcharge
from staff.tests.factories import StaffFactory

__all__ = (
    'PenaltyFactory',
    'SurchargeFactory',
)


class PenaltyFactory(DjangoModelFactory):
    class Meta:
        model = Penalty

    staff = factory.SubFactory(StaffFactory)
    reason = factory.Faker('sentence')
    created_at = factory.Faker('date_time')


class SurchargeFactory(DjangoModelFactory):
    class Meta:
        model = Surcharge

    staff = factory.SubFactory(StaffFactory)
    reason = factory.Faker('sentence')
    amount = factory.Faker('random_int', min=100, max=10000)
    created_at = factory.Faker('date_time')
