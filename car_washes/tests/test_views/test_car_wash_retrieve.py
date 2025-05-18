import pytest
from django.urls import reverse
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.test import APIClient

from car_washes.tests.factories import (
    CarWashFactory, CarWashServiceFactory,
    CarWashServicePriceFactory,
)


@pytest.mark.django_db
def test_car_wash_not_found():
    client = APIClient()
    url = reverse('car-washes:detail-update-delete', args=(53443,))

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data == {
        "type": "client_error",
        "errors": [
            {
                "code": "car_wash_not_found",
                "detail": _("car wash was not found"),
            }
        ]
    }


@pytest.mark.django_db
def test_car_wash_without_services():
    client = APIClient()
    car_wash = CarWashFactory()
    url = reverse('car-washes:detail-update-delete', args=(car_wash.id,))

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": car_wash.id,
        "name": car_wash.name,
        "car_transporters_comfort_class_car_washing_price":
            car_wash.comfort_class_car_washing_price,
        "car_transporters_business_class_car_washing_price":
            car_wash.business_class_car_washing_price,
        "car_transporters_van_washing_price": car_wash.van_washing_price,
        "car_transporters_and_washers_comfort_class_price":
            car_wash.car_transporters_and_washers_comfort_class_price,
        "car_transporters_and_washers_business_class_price":
            car_wash.car_transporters_and_washers_business_class_price,
        "car_transporters_and_washers_van_price":
            car_wash.car_transporters_and_washers_van_price,
        "windshield_washer_price_per_bottle":
            car_wash.windshield_washer_price_per_bottle,
        "is_hidden": car_wash.is_hidden,
        "services": [],
        "created_at": response.data["created_at"],
        "updated_at": response.data["updated_at"],
    }


@pytest.mark.django_db
def test_car_wash_with_services():
    client = APIClient()
    service_price = CarWashServicePriceFactory()
    car_wash = service_price.car_wash
    url = reverse('car-washes:detail-update-delete', args=(car_wash.id,))

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": car_wash.id,
        "name": car_wash.name,
        "car_transporters_comfort_class_car_washing_price":
            car_wash.comfort_class_car_washing_price,
        "car_transporters_business_class_car_washing_price":
            car_wash.business_class_car_washing_price,
        "car_transporters_van_washing_price": car_wash.van_washing_price,
        "car_transporters_and_washers_comfort_class_price":
            car_wash.car_transporters_and_washers_comfort_class_price,
        "car_transporters_and_washers_business_class_price":
            car_wash.car_transporters_and_washers_business_class_price,
        "car_transporters_and_washers_van_price":
            car_wash.car_transporters_and_washers_van_price,
        "windshield_washer_price_per_bottle":
            car_wash.windshield_washer_price_per_bottle,
        "is_hidden": car_wash.is_hidden,
        "services": [
            {
                "id": str(service_price.service.id),
                "name": service_price.service.name,
                "is_countable": service_price.service.is_countable,
                "max_count": service_price.service.max_count,
                "parent": {
                    "id": service_price.service.parent.id,
                    "name": service_price.service.parent.name,
                } if service_price.service.parent else None,
                'is_dry_cleaning': service_price.service.is_dry_cleaning,
                "price": service_price.price,
            }
        ],
        "created_at": response.data["created_at"],
        "updated_at": response.data["updated_at"],
    }


[{
     'id': '97751bc2-fcb8-4886-9e53-42fc5343c1b4',
    'name': 'Tabitha Dougherty',
     'is_countable': True,
    'price': 894, 'parent': None, 'max_count': 1000000
 }]
