import datetime
from dataclasses import dataclass

from car_washes.selectors import (
    CarWashServiceDto,
    get_car_wash_by_id,
    get_flatten_specific_car_wash_services,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashRetrieveResult:
    id: int
    name: str
    car_transporters_comfort_class_car_washing_price: int
    car_transporters_business_class_car_washing_price: int
    car_transporters_van_washing_price: int
    car_transporters_and_washers_comfort_class_price: int
    car_transporters_and_washers_business_class_price: int
    car_transporters_and_washers_van_price: int
    windshield_washer_price_per_bottle: int
    is_hidden: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    services: list[CarWashServiceDto]


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashRetrieveUseCase:
    car_wash_id: int

    def execute(self):
        car_wash = get_car_wash_by_id(self.car_wash_id)
        car_wash_services = get_flatten_specific_car_wash_services(
            car_wash_id=self.car_wash_id,
        )

        return CarWashRetrieveResult(
            id=car_wash.id,
            name=car_wash.name,
            car_transporters_comfort_class_car_washing_price=(
                car_wash.comfort_class_car_washing_price
            ),
            car_transporters_business_class_car_washing_price=(
                car_wash.business_class_car_washing_price
            ),
            car_transporters_van_washing_price=(
                car_wash.van_washing_price
            ),
            car_transporters_and_washers_comfort_class_price=(
                car_wash.car_transporters_and_washers_comfort_class_price
            ),
            car_transporters_and_washers_business_class_price=(
                car_wash.car_transporters_and_washers_business_class_price
            ),
            car_transporters_and_washers_van_price=(
                car_wash.car_transporters_and_washers_van_price
            ),
            windshield_washer_price_per_bottle=(
                car_wash.windshield_washer_price_per_bottle
            ),
            is_hidden=car_wash.is_hidden,
            created_at=car_wash.created_at,
            updated_at=car_wash.updated_at,
            services=car_wash_services,
        )
