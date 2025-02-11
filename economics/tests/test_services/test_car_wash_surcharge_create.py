import pytest

from car_washes.exceptions import CarWashNotFoundError
from car_washes.tests.factories import CarWashFactory
from economics.services.car_washes.surcharges import (
    CarWashSurchargeCreateInteractor
)


@pytest.mark.django_db
def test_car_wash_surcharge_create_successfully():
    car_wash = CarWashFactory()
    interactor = CarWashSurchargeCreateInteractor(
        car_wash_id=car_wash.id,
        reason='reason',
        amount=100,
    )

    surcharge = interactor.execute()

    assert surcharge.car_wash_id == car_wash.id
    assert surcharge.reason == 'reason'
    assert surcharge.amount == 100
    assert surcharge.created_at is not None
    assert surcharge.id is not None


@pytest.mark.django_db
def test_car_wash_surcharge_create_car_wash_does_not_exist():
    interactor = CarWashSurchargeCreateInteractor(
        car_wash_id=1231432,
        reason='reason',
        amount=100,
    )
    with pytest.raises(CarWashNotFoundError):
        interactor.execute()
