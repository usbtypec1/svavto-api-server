from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from uuid import UUID

from django.db import transaction
from django.db.models import Q, QuerySet
from typing_extensions import TypedDict

from car_washes.models import CarWash, CarWashServicePrice
from shifts.models import CarToWash, CarToWashAdditionalService
from shifts.use_cases.transferred_car_create import compute_car_transfer_price


@dataclass(frozen=True, slots=True, kw_only=True)
class AdditionalServiceDto:
    id: UUID
    name: str
    count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CarDto:
    id: int
    shift_id: int
    is_extra_shift: bool
    number: str
    car_wash_id: int | None
    car_wash_name: str | None
    class_type: str
    wash_type: str
    windshield_washer_type: str
    windshield_washer_refilled_bottle_percentage: int
    additional_services: list[AdditionalServiceDto]


class ItemAdditionalService(TypedDict):
    id: UUID
    count: int


class Item(TypedDict):
    shift_id: int
    car_wash_id: int
    car_number: str
    class_type: str
    wash_type: str
    windshield_washer_type: str
    windshield_washer_refilled_bottle_percentage: int
    additional_services: list[ItemAdditionalService]


def get_cars(items: Iterable[Item]) -> list[CarDto]:
    shift_ids = [item['shift_id'] for item in items]

    cars: QuerySet[CarToWash] = (
        CarToWash.objects.select_related('car_wash', 'shift')
        .prefetch_related('additional_services')
        .filter(shift_id__in=shift_ids)
    )

    result: list[CarDto] = []

    for car in cars:
        additional_services = [
            AdditionalServiceDto(
                id=service.service_id,
                name=service.service.name,
                count=service.count,
            )
            for service in car.additional_services.all()
        ]

        result.append(
            CarDto(
                id=car.id,
                shift_id=car.shift_id,
                is_extra_shift=car.shift.is_extra,
                number=car.number,
                car_wash_id=car.car_wash.id if car.car_wash else None,
                car_wash_name=car.car_wash.name if car.car_wash else None,
                class_type=car.car_class,
                wash_type=car.wash_type,
                windshield_washer_type=car.windshield_washer_type,
                windshield_washer_refilled_bottle_percentage=car
                .windshield_washer_refilled_bottle_percentage,
                additional_services=additional_services
            )
        )

    return result


type ShiftIdAndCarNumber = tuple[int, str]


class BatchEditService:

    def __init__(self, items: Iterable[Item]):
        self.__items = tuple(items)
        self.__cars = get_cars(self.__items)
        self.__extra_shift_ids = {
            car.shift_id
            for car in self.__cars
            if car.is_extra_shift
        }
        self.__shift_id_and_number_to_item = (
            self.get_shift_id_and_number_to_item()
        )
        self.__new_cars = set(self.__shift_id_and_number_to_item)
        self.__existing_cars = self.get_existing_cars()

    def get_shift_id_and_number_to_item(self) -> dict[
        ShiftIdAndCarNumber, Item]:
        return {
            (item['shift_id'], item['car_number']): item
            for item in self.__items
        }

    def get_existing_cars(self) -> set[ShiftIdAndCarNumber]:
        return {(car.shift_id, car.number) for car in self.__cars}

    def get_cars_to_delete(self) -> set[ShiftIdAndCarNumber]:
        return self.__existing_cars.difference(self.__new_cars)

    def get_cars_to_create(self) -> set[ShiftIdAndCarNumber]:
        return self.__new_cars.difference(self.__existing_cars)

    def get_cars_to_update(self) -> set[ShiftIdAndCarNumber]:
        return self.__new_cars.intersection(self.__existing_cars)

    def delete_cars(self):
        if not self.get_cars_to_delete():
            return
        filter_q = Q()
        for shift_id, car_number in self.get_cars_to_delete():
            filter_q |= Q(shift_id=shift_id, number=car_number)
        CarToWash.objects.filter(filter_q).delete()

    def update_cars(self):
        for car in self.get_cars_to_update():
            item = self.__shift_id_and_number_to_item[car]
            transferred_car = CarToWash.objects.get(
                shift_id=item['shift_id'],
                number=item['car_number'],
            )
            transferred_car.car_wash_id = item['car_wash_id']
            transferred_car.car_class = item['class_type']
            transferred_car.wash_type = item['wash_type']
            transferred_car.windshield_washer_type = item[
                'windshield_washer_type']
            transferred_car.windshield_washer_refilled_bottle_percentage = (
                item['windshield_washer_refilled_bottle_percentage']
            )
            CarToWashAdditionalService.objects.filter(
                car=transferred_car
                ).delete()
            service_ids = [
                service['id'] for service in item['additional_services']
            ]
            service_prices = CarWashServicePrice.objects.filter(
                service_id__in=service_ids,
            )
            service_id_to_price = {
                service_price.service_id: service_price.price
                for service_price in service_prices
            }
            additional_services = []
            for service in item['additional_services']:
                if service['id'] not in service_id_to_price:
                    continue
                price = service_id_to_price[service['id']]
                additional_services.append(
                    CarToWashAdditionalService(
                        car_id=transferred_car.id,
                        service_id=service['id'],
                        count=service['count'],
                        price=price,
                    )
                )
            CarToWashAdditionalService.objects.bulk_create(
                additional_services
            )

    @lru_cache(maxsize=100)
    def get_car_wash_by_id(self, car_wash_id: int) -> CarWash | None:
        return CarWash.objects.filter(id=car_wash_id).first()

    def create_cars(self):
        for car in self.get_cars_to_create():
            item = self.__shift_id_and_number_to_item[car]
            car_wash = self.get_car_wash_by_id(item['car_wash_id'])
            if car_wash is None:
                continue
            transfer_price = compute_car_transfer_price(
                class_type=item['class_type'],
                wash_type=item['wash_type'],
                is_extra_shift=item['shift_id'] in self.__extra_shift_ids,
            )
            with transaction.atomic():
                transferred_car = CarToWash(
                    shift_id=item['shift_id'],
                    car_wash_id=item['car_wash_id'],
                    number=item['car_number'],
                    car_class=item['class_type'],
                    wash_type=item['wash_type'],
                    windshield_washer_type=item['windshield_washer_type'],
                    windshield_washer_refilled_bottle_percentage=(
                        item['windshield_washer_refilled_bottle_percentage']
                    ),
                    transfer_price=transfer_price,
                    comfort_class_car_washing_price=car_wash
                    .comfort_class_car_washing_price,
                    business_class_car_washing_price=car_wash
                    .business_class_car_washing_price,
                    van_washing_price=car_wash.van_washing_price,
                    windshield_washer_price_per_bottle=car_wash
                    .windshield_washer_price_per_bottle,
                )
                transferred_car.full_clean()
                transferred_car.save()

                service_ids = [
                    service['id'] for service in item['additional_services']
                ]

                service_prices = CarWashServicePrice.objects.filter(
                    service_id__in=service_ids,
                )
                service_id_to_price = {
                    service_price.service_id: service_price.price
                    for service_price in service_prices
                }

                additional_services = []
                for service in item['additional_services']:
                    if service['id'] not in service_id_to_price:
                        continue
                    price = service_id_to_price[service['id']]
                    additional_services.append(
                        CarToWashAdditionalService(
                            car_id=transferred_car.id,
                            service_id=service['id'],
                            count=service['count'],
                            price=price,
                        )
                    )
                CarToWashAdditionalService.objects.bulk_create(
                    additional_services
                )
