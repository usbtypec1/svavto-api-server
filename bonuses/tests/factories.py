import factory
from factory.django import DjangoModelFactory

from bonuses.models import BonusSettings


class BonusSettingsFactory(DjangoModelFactory):
    class Meta:
        model = BonusSettings

    min_cars_count = factory.Faker("random_int", min=1, max=100)
    bonus_amount = factory.Faker("random_int", min=1, max=100)
