import random

import pytest
from django.core.management import call_command

from shifts.use_cases.transferred_car_create import TransferredCarCreateUseCase
from shifts.tests.factories import ShiftFactory
from shifts.models import CarToWash
from car_washes.tests.factories import (
    CarWashFactory,
    CarWashServiceFactory,
    CarWashServicePriceFactory,
)


@pytest.fixture(scope="session", autouse=True)
def run_management_command(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("init_staff_service_prices")


@pytest.mark.django_db
def test_transferred_car_successully_created_without_additional_services():
    shift = ShiftFactory(finished_at=None, car_wash=CarWashFactory())

    transferred_car = TransferredCarCreateUseCase(
        staff_id=shift.staff.id,
        number="а123ыв121",
        car_class=CarToWash.CarType.COMFORT,
        wash_type=CarToWash.WashType.PLANNED,
        windshield_washer_type=CarToWash.WindshieldWasherType.ANTIFREEZE,
        windshield_washer_refilled_bottle_percentage=100,
        additional_services=[],
    ).execute()

    assert transferred_car.car_wash_id == shift.car_wash.id
    assert len(transferred_car.additional_services) == 0
    assert transferred_car.class_type == CarToWash.CarType.COMFORT
    assert transferred_car.wash_type == CarToWash.WashType.PLANNED
    assert (
        transferred_car.windshield_washer_type
        == CarToWash.WindshieldWasherType.ANTIFREEZE
    )
    assert transferred_car.windshield_washer_refilled_bottle_percentage == 100
    assert transferred_car.number == "а123ыв121"


@pytest.mark.django_db
def test_transferred_car_successully_created_with_additional_services():
    car_wash = CarWashFactory()
    shift = ShiftFactory(finished_at=None, car_wash=car_wash)
    service_prices = CarWashServicePriceFactory.create_batch(5, car_wash=car_wash)
    additional_services = [
        {"id": service_price.service.id, "count": random.randint(1, 10)}
        for service_price in service_prices
    ]

    transferred_car = TransferredCarCreateUseCase(
        staff_id=shift.staff.id,
        number="а123ыв152",
        car_class=CarToWash.CarType.COMFORT,
        wash_type=CarToWash.WashType.PLANNED,
        windshield_washer_type=CarToWash.WindshieldWasherType.ANTIFREEZE,
        windshield_washer_refilled_bottle_percentage=50,
        additional_services=additional_services,
    ).execute()

    assert transferred_car.car_wash_id == shift.car_wash.id
    assert transferred_car.class_type == CarToWash.CarType.COMFORT
    assert transferred_car.wash_type == CarToWash.WashType.PLANNED
    assert (
        transferred_car.windshield_washer_type
        == CarToWash.WindshieldWasherType.ANTIFREEZE
    )
    assert transferred_car.windshield_washer_refilled_bottle_percentage == 50
    assert transferred_car.number == "а123ыв152"
    assert len(transferred_car.additional_services) == len(additional_services)
