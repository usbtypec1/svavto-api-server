import datetime

import pytest

from bonuses.services import BonusAmountComputeInteractor
from bonuses.tests.factories import BonusSettingsFactory
from shifts.tests.factories import ShiftFactory, TransferredCarFactory


@pytest.mark.django_db
def test_shift_is_test():
    shift = ShiftFactory(is_test=True)

    result = BonusAmountComputeInteractor(shift=shift).execute()

    assert result == 0


@pytest.mark.django_db
def test_shift_is_extra():
    shift = ShiftFactory(is_test=False, is_extra=True)

    result = BonusAmountComputeInteractor(shift=shift).execute()

    assert result == 0


@pytest.mark.django_db
def test_not_weekend():
    weekend = datetime.date(2025, 4, 6)
    shift = ShiftFactory(is_test=False, is_extra=False, date=weekend)

    result = BonusAmountComputeInteractor(shift=shift).execute()

    assert result == 0


@pytest.mark.django_db
def test_no_bonus_settings():
    shift = ShiftFactory()

    result = (
        BonusAmountComputeInteractor(shift=shift)
        .is_bonus_settings_exists()
    )

    assert not result


@pytest.mark.django_db
def test_no_cars():
    shift = ShiftFactory()

    result = (
        BonusAmountComputeInteractor(shift=shift)
        .get_shift_transferred_cars_count()
    )

    assert result == 0


@pytest.mark.django_db
def test_not_enough_cars():
    BonusSettingsFactory(min_cars_count=2)
    shift = ShiftFactory()
    TransferredCarFactory(shift=shift)

    result = (
        BonusAmountComputeInteractor(shift=shift)
        .is_enough_cars()
    )

    assert not result


@pytest.mark.django_db
def test_enough_cars():
    BonusSettingsFactory(min_cars_count=2)
    shift = ShiftFactory()
    TransferredCarFactory(shift=shift)
    TransferredCarFactory(shift=shift)

    result = (
        BonusAmountComputeInteractor(shift=shift)
        .is_enough_cars()
    )

    assert result


@pytest.mark.django_db
def test_staff_excluded():
    shift = ShiftFactory()
    BonusSettingsFactory().excluded_staff.add(shift.staff)

    result = (
        BonusAmountComputeInteractor(shift=shift)
        .is_staff_excluded()
    )

    assert result


@pytest.mark.django_db
def test_staff_not_excluded():
    shift = ShiftFactory()
    BonusSettingsFactory()

    result = (
        BonusAmountComputeInteractor(shift=shift)
        .is_staff_excluded()
    )

    assert not result


@pytest.mark.django_db
def test_bonus_amount_is_not_zero():
    BonusSettingsFactory(min_cars_count=2, bonus_amount=100)
    weekday = datetime.date(2025, 4, 5)
    shift = ShiftFactory(is_test=False, is_extra=False, date=weekday)
    TransferredCarFactory(shift=shift)
    TransferredCarFactory(shift=shift)

    result = (
        BonusAmountComputeInteractor(shift=shift)
        .execute()
    )

    assert result == 100


if __name__ == '__main__':
    pytest.main()
