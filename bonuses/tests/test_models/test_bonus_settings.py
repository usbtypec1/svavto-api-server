import pytest

from bonuses.tests.factories import BonusSettingsFactory


@pytest.mark.django_db
def test_bonus_enabled():
    bonus_settings = BonusSettingsFactory(min_cars_count=1, bonus_amount=100)
    assert bonus_settings.is_bonus_enabled


@pytest.mark.django_db
def test_bonus_not_enabled():
    items = [
        BonusSettingsFactory(min_cars_count=0, bonus_amount=100),
        BonusSettingsFactory(min_cars_count=1, bonus_amount=0),
        BonusSettingsFactory(min_cars_count=0, bonus_amount=0),
    ]
    for item in items:
        assert not item.is_bonus_enabled
