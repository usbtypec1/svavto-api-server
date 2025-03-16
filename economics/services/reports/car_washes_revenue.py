import datetime
from collections import defaultdict
from collections.abc import Iterable

from economics.selectors import (
    CarWashPenaltiesAndSurchargesByDate,
    get_car_wash_penalties_and_surcharges_for_period,
)
from shifts.models import CarToWash
from shifts.selectors import (
    CarToWashAdditionalServiceDTO,
    CarToWashDTO,
    get_cars_to_wash_for_period,
)


__all__ = ("get_car_washes_sales_report",)


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


def merge_cars_to_wash_to_statistics(
    cars: Iterable[CarToWashDTO],
) -> dict:
    cars_statistics = {
        "comfort_cars_washed_count": 0,
        "business_cars_washed_count": 0,
        "van_cars_washed_count": 0,
        "windshield_washer_refilled_bottle_count": 0,
        "total_cost": 0,
        "additional_services": [],
    }

    car_class_counts: dict[CarToWash.CarType | str, str] = {
        CarToWash.CarType.COMFORT: "comfort_cars_washed_count",
        CarToWash.CarType.BUSINESS: "business_cars_washed_count",
        CarToWash.CarType.VAN: "van_cars_washed_count",
    }

    for car in cars:
        if car.car_class in car_class_counts:
            cars_statistics[car_class_counts[car.car_class]] += 1
        else:
            raise ValueError(f"Unknown car class: {car.car_class}")

        cars_statistics["windshield_washer_refilled_bottle_count"] += (
            car.windshield_washer_refilled_bottle_count
        )
        cars_statistics["additional_services"] = merge_additional_services(
            cars_statistics["additional_services"] + car.additional_services
        )
        cars_statistics["total_cost"] += compute_total_cost(car)

    return cars_statistics


def group_cars_to_wash_by_shift_date(
    cars_to_wash: Iterable[CarToWashDTO],
    penalties_and_surcharges: Iterable[CarWashPenaltiesAndSurchargesByDate],
) -> list[dict]:
    shift_date_to_cars = defaultdict(list)

    for car in cars_to_wash:
        shift_date_to_cars[car.shift_date].append(car)

    shift_date_to_penalties_and_surcharges = {
        penalty_and_surcharge.date: penalty_and_surcharge
        for penalty_and_surcharge in penalties_and_surcharges
    }

    all_dates = set(shift_date_to_cars).union(shift_date_to_penalties_and_surcharges)

    result = []

    for date in all_dates:
        cars = shift_date_to_cars.get(date, [])
        penalty_and_surcharge = shift_date_to_penalties_and_surcharges.get(date)

        if penalty_and_surcharge is None:
            penalties_amount = 0
            surcharges_amount = 0
        else:
            penalties_amount = penalty_and_surcharge.penalties_amount
            surcharges_amount = penalty_and_surcharge.surcharges_amount

        cars_to_wash_to_statistics = merge_cars_to_wash_to_statistics(cars)
        total_cost = (
            cars_to_wash_to_statistics.get("total_cost", 0)
            - penalties_amount
            + surcharges_amount
        )

        result.append(
            {
                "shift_date": date,
                **cars_to_wash_to_statistics,
                "total_cost": total_cost,
                "penalties_amount": penalties_amount,
                "surcharges_amount": surcharges_amount,
            }
        )
    return result


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
    car_wash_penalties_and_surcharges = (
        get_car_wash_penalties_and_surcharges_for_period(
            car_wash_ids=car_wash_ids,
            from_date=from_date,
            to_date=to_date,
        )
    )

    return group_cars_to_wash_by_shift_date(
        cars_to_wash=cars_to_wash,
        penalties_and_surcharges=car_wash_penalties_and_surcharges,
    )
