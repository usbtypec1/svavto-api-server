import random

import pytest

from shifts.use_cases.transferred_car_update import TransferredCarUpdateUseCase
from shifts.tests.factories import (
    TransferredCarFactory,
    TransferredCarAdditionalServiceFactory,
)
from shifts.models.cars_to_wash import CarToWash
from car_washes.tests.factories import (
    CarWashFactory,
    CarWashServicePriceFactory,
)


@pytest.mark.parametrize(
    "old_number, new_number",
    [
        ("а234ыв121", "а123ыв121"),
        ("р234ыв412", "р123ыв412"),
        ("а234ыв121", "а234ыв523"),
    ],
)
@pytest.mark.django_db
def test_transferred_car_update_number(old_number, new_number):
    transferred_car = TransferredCarFactory(number=old_number)

    TransferredCarUpdateUseCase(
        car_id=transferred_car.id,
        number=new_number,
    ).execute()

    transferred_car.refresh_from_db()
    assert transferred_car.number == new_number


@pytest.mark.parametrize(
    "old_class_type, new_class_type",
    [
        (CarToWash.CarType.COMFORT, CarToWash.CarType.BUSINESS),
        (CarToWash.CarType.BUSINESS, CarToWash.CarType.COMFORT),
        (CarToWash.CarType.COMFORT, CarToWash.CarType.COMFORT),
        (CarToWash.CarType.BUSINESS, CarToWash.CarType.BUSINESS),
        (CarToWash.CarType.COMFORT, CarToWash.CarType.VAN),
        (CarToWash.CarType.VAN, CarToWash.CarType.COMFORT),
        (CarToWash.CarType.BUSINESS, CarToWash.CarType.VAN),
        (CarToWash.CarType.VAN, CarToWash.CarType.BUSINESS),
    ],
)
@pytest.mark.django_db
def test_transferred_car_update_class_type(old_class_type, new_class_type):
    transferred_car = TransferredCarFactory(car_class=old_class_type)

    TransferredCarUpdateUseCase(
        car_id=transferred_car.id,
        class_type=new_class_type,
    ).execute()

    transferred_car.refresh_from_db()
    assert transferred_car.car_class == new_class_type


@pytest.mark.parametrize(
    "old_wash_type, new_wash_type",
    [
        (CarToWash.WashType.PLANNED, CarToWash.WashType.URGENT),
        (CarToWash.WashType.URGENT, CarToWash.WashType.PLANNED),
        (CarToWash.WashType.PLANNED, CarToWash.WashType.PLANNED),
        (CarToWash.WashType.URGENT, CarToWash.WashType.URGENT),
    ],
)
@pytest.mark.django_db
def test_transferred_car_update_wash_type(
    old_wash_type,
    new_wash_type,
):
    transferred_car = TransferredCarFactory(wash_type=old_wash_type)

    TransferredCarUpdateUseCase(
        car_id=transferred_car.id,
        wash_type=new_wash_type,
    ).execute()

    transferred_car.refresh_from_db()
    assert transferred_car.wash_type == new_wash_type


@pytest.mark.django_db
def test_transferred_car_update_car_wash():
    car_wash_1 = CarWashFactory()
    car_wash_2 = CarWashFactory()
    transferred_car = TransferredCarFactory(car_wash=car_wash_1)

    TransferredCarUpdateUseCase(
        car_id=transferred_car.id, car_wash_id=car_wash_2.id
    ).execute()

    transferred_car.refresh_from_db()
    assert transferred_car.car_wash_id != car_wash_1.id
    assert transferred_car.car_wash_id == car_wash_2.id


@pytest.mark.django_db
def test_transferred_car_update_windshield_washer_type():
    transferred_car = TransferredCarFactory(
        windshield_washer_type=CarToWash.WindshieldWasherType.ANTIFREEZE,
        windshield_washer_refilled_bottle_percentage=50,
    )

    old_windshield_washer_type = transferred_car.windshield_washer_type
    TransferredCarUpdateUseCase(
        car_id=transferred_car.id,
        windshield_washer_type=CarToWash.WindshieldWasherType.WATER,
    ).execute()

    transferred_car.refresh_from_db()
    assert transferred_car.windshield_washer_type != old_windshield_washer_type
    assert (
        transferred_car.windshield_washer_type == CarToWash.WindshieldWasherType.WATER
    )
    assert transferred_car.windshield_washer_refilled_bottle_percentage == 0


@pytest.mark.parametrize(
    "old_windshield_washer_refilled_bottle_percentage, new_windshield_washer_refilled_bottle_percentage",
    [
        (50, 0),
        (0, 50),
        (50, 100),
        (100, 50),
    ],
)
@pytest.mark.django_db
def test_transferred_car_update_windshield_washer_refilled_bottle_percentage(
    old_windshield_washer_refilled_bottle_percentage,
    new_windshield_washer_refilled_bottle_percentage,
):
    transferred_car = TransferredCarFactory(
        windshield_washer_refilled_bottle_percentage=old_windshield_washer_refilled_bottle_percentage,
    )

    TransferredCarUpdateUseCase(
        car_id=transferred_car.id,
        windshield_washer_refilled_bottle_percentage=new_windshield_washer_refilled_bottle_percentage,
    ).execute()

    transferred_car.refresh_from_db()
    assert (
        transferred_car.windshield_washer_refilled_bottle_percentage
        != old_windshield_washer_refilled_bottle_percentage
    )
    assert (
        transferred_car.windshield_washer_refilled_bottle_percentage
        == new_windshield_washer_refilled_bottle_percentage
    )


@pytest.mark.django_db
def test_transferred_car_update_additional_services_set_empty():
    transferred_car = TransferredCarFactory()
    additional_services = TransferredCarAdditionalServiceFactory.create_batch(
        5, car=transferred_car
    )
    old_additional_services_count = len(additional_services)

    additional_services = TransferredCarUpdateUseCase(
        car_id=transferred_car.id,
        additional_services=[],
    ).execute()

    transferred_car.refresh_from_db()
    assert old_additional_services_count == 5
    assert len(additional_services) == 0


@pytest.mark.django_db
def test_transferred_car_update_additional_services_set_new():
    car_wash = CarWashFactory()
    transferred_car = TransferredCarFactory(car_wash=car_wash)
    car_wash_price_services = CarWashServicePriceFactory.create_batch(
        5, car_wash=car_wash
    )
    additional_services = TransferredCarUpdateUseCase(
        car_id=transferred_car.id,
        additional_services=[
            {
                "id": car_wash_price_service.service.id,
                "count": random.randint(1, 10),
            }
            for car_wash_price_service in car_wash_price_services
        ],
    ).execute()

    transferred_car.refresh_from_db()
    assert len(additional_services) == 5
