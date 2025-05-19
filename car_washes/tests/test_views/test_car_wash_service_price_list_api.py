import pytest

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from car_washes.tests.factories import CarWashFactory, CarWashServicePriceFactory
from car_washes.models import CarWash


@pytest.fixture
def car_wash() -> CarWash:
    return CarWashFactory()


@pytest.mark.django_db
def test_car_wash_without_service_prices(car_wash):
    url = reverse("car-washes:service-prices", kwargs={"car_wash_id": car_wash.id})
    client = APIClient()

    response = client.get(url)

    assert response.status_code == 200
    assert response.json() == {
        "car_wash_id": car_wash.id,
        "car_wash_name": car_wash.name,
        "planned_car_transfer_price": car_wash.comfort_class_car_washing_price,
        "business_car_transfer_price": car_wash.business_class_car_washing_price,
        "van_transfer_price": car_wash.van_washing_price,
        "windshield_washer_bottle_price": car_wash.windshield_washer_price_per_bottle,
        "services": [],
    }


@pytest.mark.django_db
def test_car_wash_with_service_prices(car_wash):
    service_prices = CarWashServicePriceFactory.create_batch(3, car_wash=car_wash)
    url = reverse("car-washes:service-prices", kwargs={"car_wash_id": car_wash.id})
    client = APIClient()

    response = client.get(url)

    assert response.status_code == 200
    assert response.json() == {
        "car_wash_id": car_wash.id,
        "car_wash_name": car_wash.name,
        "planned_car_transfer_price": car_wash.comfort_class_car_washing_price,
        "business_car_transfer_price": car_wash.business_class_car_washing_price,
        "van_transfer_price": car_wash.van_washing_price,
        "windshield_washer_bottle_price": car_wash.windshield_washer_price_per_bottle,
        "services": [
            {
                "id": str(service_price.service.id),
                "name": service_price.service.name,
                "price": service_price.price,
                "created_at": timezone.make_aware(
                    timezone.make_naive(service_price.created_at),
                    timezone.get_current_timezone(),
                ).isoformat(),
                "updated_at": timezone.make_aware(
                    timezone.make_naive(service_price.updated_at),
                    timezone.get_current_timezone(),
                ).isoformat(),
            }
            for service_price in service_prices
        ],
    }


@pytest.mark.django_db
def test_car_wash_not_found():
    url = reverse("car-washes:service-prices", kwargs={"car_wash_id": 53454323})
    client = APIClient()

    response = client.get(url)

    assert response.status_code == 404
    assert response.json() == {
        "type": "client_error",
        "errors": [
            {
                "code": "car_wash_not_found",
                "detail": "Мойка не найдена",
            },
        ],
    }
