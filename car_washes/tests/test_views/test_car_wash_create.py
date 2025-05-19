import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from car_washes.tests.factories import CarWashFactory


@pytest.mark.django_db
def test_car_wash_successfully_created():
    client = APIClient()
    url = reverse('car-washes:wash-list-create')
    data = {
        "name": "Test Car Wash",
        "car_transporters_comfort_class_car_washing_price": 100,
        "car_transporters_business_class_car_washing_price": 200,
        "car_transporters_van_washing_price": 300,
        "car_transporters_and_washers_comfort_class_price": 400,
        "car_transporters_and_washers_business_class_price": 500,
        "car_transporters_and_washers_van_price": 600,
        "windshield_washer_price_per_bottle": 700,
        "is_hidden": False,
    }

    response = client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data
    assert "created_at" in response.data
    assert "updated_at" in response.data
    assert response.data == {
        "id": response.data["id"],
        "name": "Test Car Wash",
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


@pytest.mark.django_db
def test_car_wash_name_duplicated():
    car_wash = CarWashFactory()

    client = APIClient()
    url = reverse('car-washes:wash-list-create')
    data = {
        "name": car_wash.name,
        "car_transporters_comfort_class_car_washing_price": 100,
        "car_transporters_business_class_car_washing_price": 200,
        "car_transporters_van_washing_price": 300,
        "car_transporters_and_washers_comfort_class_price": 400,
        "car_transporters_and_washers_business_class_price": 500,
        "car_transporters_and_washers_van_price": 600,
        "windshield_washer_price_per_bottle": 700,
        "is_hidden": False,
    }

    response = client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_409_CONFLICT
