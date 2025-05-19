import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from car_washes.tests.factories import CarWashFactory


@pytest.mark.django_db
def test_single_car_wash():
    client = APIClient()
    url = reverse('car-washes:wash-list-create')
    car_wash = CarWashFactory()

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        'car_washes': [
            {
                'id': car_wash.id,
                'name': car_wash.name,
                'car_transporters_comfort_class_car_washing_price':
                    car_wash.comfort_class_car_washing_price,
                'car_transporters_business_class_car_washing_price':
                    car_wash.business_class_car_washing_price,
                'car_transporters_van_washing_price':
                    car_wash.van_washing_price,
                'car_transporters_and_washers_comfort_class_price':
                    car_wash.car_transporters_and_washers_comfort_class_price,
                'car_transporters_and_washers_business_class_price':
                    car_wash.car_transporters_and_washers_business_class_price,
                'car_transporters_and_washers_van_price':
                    car_wash.car_transporters_and_washers_van_price,
                'windshield_washer_price_per_bottle':
                    car_wash.windshield_washer_price_per_bottle,
                'is_hidden': car_wash.is_hidden,
                'created_at':
                    timezone.make_aware(
                        timezone.make_naive(car_wash.created_at)
                    ).isoformat(),
                'updated_at': timezone.make_aware(
                    timezone.make_naive(car_wash.updated_at)
                ).isoformat(),
            }
        ]
    }


@pytest.mark.django_db
def test_no_car_washes():
    client = APIClient()
    url = reverse('car-washes:wash-list-create')

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        'car_washes': []
    }


@pytest.mark.django_db
def test_exclude_hidden():
    client = APIClient()
    url = reverse('car-washes:wash-list-create')
    CarWashFactory(is_hidden=True)

    response = client.get(url, {'include_hidden': False})

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        'car_washes': []
    }
