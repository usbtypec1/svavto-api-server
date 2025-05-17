import datetime
from dataclasses import dataclass
from typing import TypedDict

from car_washes.services import create_car_wash


class CarWashCreateRequestData(TypedDict):
    name: str
    car_transporters_comfort_class_car_washing_price: int
    car_transporters_business_class_car_washing_price: int
    car_transporters_van_washing_price: int
    car_transporters_and_washers_comfort_class_price: int
    car_transporters_and_washers_business_class_price: int
    car_transporters_and_washers_van_price: int
    windshield_washer_price_per_bottle: int
    is_hidden: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashCreateResult:
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


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashCreateUseCase:
    data: CarWashCreateRequestData

    def execute(self) -> CarWashCreateResult:
        car_wash = create_car_wash(
            name=self.data['name'],
            car_transporters_comfort_class_car_washing_price=(
                self.data['car_transporters_comfort_class_car_washing_price']
            ),
            car_transporters_business_class_car_washing_price=(
                self.data['car_transporters_business_class_car_washing_price']
            ),
            car_transporters_van_washing_price=(
                self.data['car_transporters_van_washing_price']
            ),
            car_transporters_and_washers_comfort_class_price=(
                self.data['car_transporters_and_washers_comfort_class_price']
            ),
            car_transporters_and_washers_business_class_price=(
                self.data['car_transporters_and_washers_business_class_price']
            ),
            car_transporters_and_washers_van_price=(
                self.data['car_transporters_and_washers_van_price']
            ),
            windshield_washer_price_per_bottle=(
                self.data['windshield_washer_price_per_bottle']
            ),
            is_hidden=self.data['is_hidden'],
        )
        return CarWashCreateResult(
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
        )
