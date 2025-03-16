import datetime

import pytest

from car_washes.exceptions import CarWashNotFoundError
from car_washes.tests.factories import CarWashFactory
from economics.services.car_washes.penalties import CarWashPenaltyCreateInteractor


@pytest.mark.django_db
def test_car_wash_penalty_create_successfully():
    car_wash = CarWashFactory()
    interactor = CarWashPenaltyCreateInteractor(
        car_wash_id=car_wash.id,
        reason="reason",
        amount=100,
        date=datetime.date(2025, 1, 1),
    )

    penalty = interactor.execute()

    assert penalty.car_wash_id == car_wash.id
    assert penalty.reason == "reason"
    assert penalty.amount == 100
    assert penalty.created_at is not None
    assert penalty.id is not None


@pytest.mark.django_db
def test_car_wash_penalty_create_car_wash_does_not_exist():
    interactor = CarWashPenaltyCreateInteractor(
        car_wash_id=1231432,
        reason="reason",
        amount=100,
        date=datetime.date(2025, 1, 1),
    )
    with pytest.raises(CarWashNotFoundError):
        interactor.execute()
