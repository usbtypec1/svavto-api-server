import datetime
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from car_washes.models import CarWash
from shifts.models import CarToWash
from shifts.selectors import (
    CarToWashAdditionalServiceDTO, CarToWashDTO, get_cars_to_wash_for_period,
)

__all__ = ('get_car_washes_sales_report',)


def compute_total_cost(car_to_wash: CarToWashDTO) -> int:
    """
    Calculate the total cost of washing a car.

    This includes the washing price, windshield washer price, 
    and the total cost of all additional services.

    Args:
        car_to_wash (CarToWashDTO): The car washing details.

    Returns:
        int: The total cost of washing the car.
    """
    additional_services_total_cost = sum(
        service.total_price for service in car_to_wash.additional_services
    )
    return (
            car_to_wash.washing_price
            + car_to_wash.windshield_washer_price
            + additional_services_total_cost
    )


def merge_additional_services(
        additional_services: Iterable[CarToWashAdditionalServiceDTO],
) -> list[CarToWashAdditionalServiceDTO]:
    service_id_to_service = {}

    for service in additional_services:
        if service.id not in service_id_to_service:
            service_id_to_service[service.id] = service
        else:
            previous_service = service_id_to_service[service.id]
            merged_service = CarToWashAdditionalServiceDTO(
                id=service.id,
                name=service.name,
                count=previous_service.count + service.count,
                total_price=previous_service.total_price + service.total_price,
                car_to_wash_id=service.car_to_wash_id,
            )
            service_id_to_service[service.id] = merged_service

    return list(service_id_to_service.values())


@dataclass(frozen=True)
class ShiftCarWashCarsToWash:
    shift_date: datetime.date
    car_wash_id: int
    cars: list[CarToWashDTO]


def merge_cars_to_wash_to_statistics(
        cars: Iterable[CarToWashDTO],
) -> dict:
    cars_statistics = {
        'comfort_cars_washed_count': 0,
        'business_cars_washed_count': 0,
        'van_cars_washed_count': 0,
        'windshield_washer_refilled_bottle_count': 0,
        'total_cost': 0,
        'additional_services': [],
    }

    car_class_counts: dict[CarToWash.CarType | str, str] = {
        CarToWash.CarType.COMFORT: 'comfort_cars_washed_count',
        CarToWash.CarType.BUSINESS: 'business_cars_washed_count',
        CarToWash.CarType.VAN: 'van_cars_washed_count',
    }

    for car in cars:
        if car.car_class in car_class_counts:
            cars_statistics[car_class_counts[car.car_class]] += 1
        else:
            raise ValueError(f'Unknown car class: {car.car_class}')

        cars_statistics['windshield_washer_refilled_bottle_count'] += (
            car.windshield_washer_refilled_bottle_count
        )
        cars_statistics['additional_services'] = merge_additional_services(
            cars_statistics['additional_services'] + car.additional_services
        )
        cars_statistics['total_cost'] += compute_total_cost(car)

    return cars_statistics


def group_cars_to_wash_by_shift_date_and_car_wash_id(
        cars_to_wash: Iterable[CarToWashDTO],
        car_wash_id_to_name: Mapping[int, str],
):
    shift_date_and_car_wash_id_to_cars = defaultdict(list)

    for car in cars_to_wash:
        key = (car.shift_date, car.car_wash_id)
        shift_date_and_car_wash_id_to_cars[key].append(car)

    return [
        {
            'shift_date': shift_date,
            'car_wash_id': car_wash_id,
            'car_wash_name': car_wash_id_to_name[car_wash_id],
            **merge_cars_to_wash_to_statistics(cars),
        }
        for (shift_date, car_wash_id), cars
        in shift_date_and_car_wash_id_to_cars.items()
    ]


def get_car_washes_sales_report(
        *,
        car_wash_ids: Iterable[int],
        from_date: datetime.date,
        to_date: datetime.date,
):
    cars_to_wash = get_cars_to_wash_for_period(
        from_date=from_date,
        to_date=to_date,
        car_wash_ids=car_wash_ids,
    )
    car_washes = CarWash.objects.values('id', 'name')
    car_wash_id_to_name = {
        car_wash['id']: car_wash['name'] for car_wash in car_washes
    }
    return group_cars_to_wash_by_shift_date_and_car_wash_id(
        cars_to_wash=cars_to_wash,
        car_wash_id_to_name=car_wash_id_to_name,
    )
