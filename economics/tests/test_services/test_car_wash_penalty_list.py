import datetime

import pytest
from django.utils import timezone

from car_washes.tests.factories import CarWashFactory
from economics.services.car_washes.penalties import (
    CarWashPenaltyListInteractor,
    CarWashPenaltyListItem,
)
from economics.tests.factories import CarWashPenaltyFactory


@pytest.mark.django_db
def test_execute_with_no_filters():
    car_wash_penalty = CarWashPenaltyFactory()
    interactor = CarWashPenaltyListInteractor(
        from_date=None,
        to_date=None,
        car_wash_ids=None,
    )

    result = interactor.execute()

    assert len(result) == 1
    assert isinstance(result[0], CarWashPenaltyListItem)
    assert result[0].id == car_wash_penalty.id


@pytest.mark.django_db
def test_execute_with_car_wash_ids_filter():
    car_wash_1 = CarWashFactory()
    car_wash_2 = CarWashFactory()
    CarWashPenaltyFactory(car_wash=car_wash_1)
    CarWashPenaltyFactory(car_wash=car_wash_2)
    interactor = CarWashPenaltyListInteractor(
        from_date=None,
        to_date=None,
        car_wash_ids=[car_wash_2.id],
    )

    result = interactor.execute()

    assert len(result) == 1
    assert result[0].car_wash_id == car_wash_2.id


@pytest.mark.django_db
def test_execute_with_from_date_filter():
    CarWashPenaltyFactory()
    CarWashPenaltyFactory()
    interactor = CarWashPenaltyListInteractor(
        from_date=timezone.now() + datetime.timedelta(days=1),
        to_date=None,
        car_wash_ids=None,
    )

    result = interactor.execute()

    assert len(result) == 0


@pytest.mark.django_db
def test_execute_with_to_date_filter():
    to_date = timezone.now() + datetime.timedelta(days=1)
    interactor = CarWashPenaltyListInteractor(
        from_date=None,
        to_date=to_date,
        car_wash_ids=None,
    )

    result = interactor.execute()

    assert len(result) == 0


@pytest.mark.django_db
def test_execute_with_no_matching_records():
    CarWashPenaltyFactory()
    interactor = CarWashPenaltyListInteractor(
        from_date=timezone.now() + datetime.timedelta(days=1),
        to_date=timezone.now() + datetime.timedelta(days=2),
        car_wash_ids=None,
    )
    result = interactor.execute()
    assert len(result) == 0
