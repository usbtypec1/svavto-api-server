from datetime import datetime, UTC

import factory
from factory.django import DjangoModelFactory

from staff.models import Staff

__all__ = ('StaffFactory',)


class StaffFactory(DjangoModelFactory):
    class Meta:
        model = Staff

    id = factory.Sequence(lambda n: n + 1000)
    full_name = factory.Faker('name')
    car_sharing_phone_number = factory.Faker('phone_number')
    console_phone_number = factory.Faker('phone_number')
    banned_at = None
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
    last_activity_at = factory.LazyFunction(lambda: datetime.now(UTC))

    class Params:
        is_banned = factory.Trait(
            banned_at=factory.LazyFunction(lambda: datetime.now(UTC))
        )
