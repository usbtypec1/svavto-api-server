import pytest
from django.urls import reverse
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.test import APIClient

from car_washes.tests.factories import CarWashFactory


@pytest.mark.django_db
def test_car_wash_not_found():
    client = APIClient()
    url = reverse('car-washes:detail-update-delete', args=(53443,))
    data = {
        "name": "Updated Car Wash",
        "car_transporters_comfort_class_car_washing_price": 100,
        "car_transporters_business_class_car_washing_price": 200,
        "car_transporters_van_washing_price": 300,
        "car_transporters_and_washers_comfort_class_price": 400,
        "car_transporters_and_washers_business_class_price": 500,
        "car_transporters_and_washers_van_price": 600,
        "windshield_washer_price_per_bottle": 700,
        "is_hidden": False,
    }

    response = client.put(url, data, format='json')

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
def test_car_wash_updated():
    client = APIClient()
    car_wash = CarWashFactory()
    url = reverse('car-washes:detail-update-delete', args=(car_wash.id,))
    data = {
        "name": "Updated Car Wash",
        "car_transporters_comfort_class_car_washing_price": 100,
        "car_transporters_business_class_car_washing_price": 200,
        "car_transporters_van_washing_price": 300,
        "car_transporters_and_washers_comfort_class_price": 400,
        "car_transporters_and_washers_business_class_price": 500,
        "car_transporters_and_washers_van_price": 600,
        "windshield_washer_price_per_bottle": 700,
        "is_hidden": False,
    }

    response = client.put(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": car_wash.id,
        "name": "Updated Car Wash",
        "car_transporters_comfort_class_car_washing_price": 100,
        "car_transporters_business_class_car_washing_price": 200,
        "car_transporters_van_washing_price": 300,
        "car_transporters_and_washers_comfort_class_price": 400,
        "car_transporters_and_washers_business_class_price": 500,
        "car_transporters_and_washers_van_price": 600,
        "windshield_washer_price_per_bottle": 700,
        "is_hidden": False,
        "created_at": response.data["created_at"],
        "updated_at": response.data["updated_at"],
    }
