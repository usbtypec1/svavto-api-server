import pytest

from car_washes.selectors import (
    CarWashServiceListItemDto,
    CarWashServiceParentDto,
)
from car_washes.tests.factories import (
    CarWashFactory, CarWashServiceFactory,
    CarWashServicePriceFactory,
)
from car_washes.use_cases.car_wash_service_list import (
    CarWashServiceListUseCase,
)


@pytest.mark.django_db
def test_all_car_wash_services_empty_list():
    result = CarWashServiceListUseCase(car_wash_ids=None).execute()

    assert result == []


@pytest.mark.django_db
def test_all_car_wash_services_has_single_service_without_parent():
    service = CarWashServiceFactory()

    result = CarWashServiceListUseCase(car_wash_ids=None).execute()

    assert result == [
        CarWashServiceListItemDto(
            id=service.id,
            name=service.name,
            is_countable=service.is_countable,
            max_count=service.max_count,
            parent=None,
        )
    ]


@pytest.mark.django_db
def test_all_car_wash_services_has_single_service_with_parent():
    service = CarWashServiceFactory(parent=CarWashServiceFactory())

    result = CarWashServiceListUseCase(car_wash_ids=None).execute()

    assert result == [
        CarWashServiceListItemDto(
            id=service.id,
            name=service.name,
            is_countable=service.is_countable,
            max_count=service.max_count,
            parent=CarWashServiceParentDto(
                id=service.parent.id,
                name=service.parent.name,
            ),
        )
    ]


@pytest.mark.django_db
def test_specific_car_wash_services_empty_list():
    CarWashServiceFactory()

    result = CarWashServiceListUseCase(car_wash_ids=[543234]).execute()

    assert result == []


@pytest.mark.django_db
def test_specific_car_wash_services_has_single_service():
    car_wash_1 = CarWashFactory()
    car_wash_2 = CarWashFactory()
    service_price_1 = CarWashServicePriceFactory(car_wash=car_wash_1)
    CarWashServicePriceFactory(car_wash=car_wash_2)

    result = CarWashServiceListUseCase(
        car_wash_ids=[service_price_1.car_wash_id],
    ).execute()

    assert result == [
        CarWashServiceListItemDto(
            id=service_price_1.service.id,
            name=service_price_1.service.name,
            is_countable=service_price_1.service.is_countable,
            max_count=service_price_1.service.max_count,
            parent=None
        )
    ]
