import pytest

from car_washes.use_cases.car_wash_service_price_list import (
    CarWashServicePriceListUseCase,
    CarWashServicePriceListDto,
    CarWashServicePriceListItemDto,
)
from car_washes.tests.factories import CarWashFactory, CarWashServicePriceFactory
from car_washes.models import CarWash
from car_washes.exceptions import CarWashNotFoundError


@pytest.fixture
def car_wash() -> CarWash:
    return CarWashFactory()


@pytest.mark.django_db
def test_car_wash_without_service_prices(car_wash):
    result = CarWashServicePriceListUseCase(car_wash_id=car_wash.id).execute()

    assert result.car_wash_id == car_wash.id
    assert result.car_wash_name == car_wash.name
    assert len(result.services) == 0


@pytest.mark.django_db
def test_car_wash_with_service_prices(car_wash):
    service_prices = CarWashServicePriceFactory.create_batch(5, car_wash=car_wash)
    expected_service_prices = [
        CarWashServicePriceListItemDto(
            id=service_price.service.id,
            name=service_price.service.name,
            price=service_price.price,
            created_at=service_price.created_at,
            updated_at=service_price.updated_at,
        )
        for service_price in service_prices
    ]

    result = CarWashServicePriceListUseCase(car_wash_id=car_wash.id).execute()

    assert result == CarWashServicePriceListDto(
        car_wash_id=car_wash.id,
        car_wash_name=car_wash.name,
        planned_car_transfer_price=car_wash.comfort_class_car_washing_price,
        business_car_transfer_price=car_wash.business_class_car_washing_price,
        van_transfer_price=car_wash.van_washing_price,
        windshield_washer_bottle_price=car_wash.windshield_washer_price_per_bottle,
        services=expected_service_prices,
    )


@pytest.mark.django_db
def test_car_wash_not_found():
    with pytest.raises(CarWashNotFoundError):
        CarWashServicePriceListUseCase(car_wash_id=1).execute()
