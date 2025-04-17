from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from django.db import transaction
from django.db.models import Q, QuerySet
from typing_extensions import TypedDict

from car_washes.models import CarWashServicePrice
from shifts.models import CarToWash, CarToWashAdditionalService


@dataclass(frozen=True, slots=True, kw_only=True)
class AdditionalServiceDto:
    id: UUID
    name: str
    count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CarDto:
    id: int
    shift_id: int
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

    additional_services: QuerySet[CarToWashAdditionalService] = (
        CarToWashAdditionalService.objects.select_related(
            'car__car_wash',
            'service',
        )
        .filter(car__shift_id__in=shift_ids)
    )

    car_map: dict[int, CarDto] = {}

    for add_serv in additional_services:
        car = add_serv.car

        if car.id not in car_map:
            car_map[car.id] = CarDto(
                id=car.id,
                shift_id=car.shift_id,
                number=car.number,
                car_wash_id=car.car_wash.id if car.car_wash else None,
                car_wash_name=car.car_wash.name if car.car_wash else None,
                class_type=car.car_class,
                wash_type=car.wash_type,
                windshield_washer_type=car.windshield_washer_type,
                windshield_washer_refilled_bottle_percentage=car
                .windshield_washer_refilled_bottle_percentage,
                additional_services=[]
            )

        car_map[car.id].additional_services.append(
            AdditionalServiceDto(
                id=add_serv.service_id,
                name=add_serv.service.name,
                count=add_serv.count,
            )
        )

    return list(car_map.values())


type ShiftIdAndCarNumber = tuple[int, str]


class BatchEditService:

    def __init__(self, items: Iterable[Item]):
        self.__items = tuple(items)
        self.__cars = get_cars(self.__items)
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
        filter_q = Q()
        for shift_id, car_number in self.get_cars_to_delete():
            filter_q |= Q(shift_id=shift_id, number=car_number)
        CarToWash.objects.filter(filter_q).delete()

    def update_cars(self):
        for car in self.get_cars_to_update():
            item = self.__shift_id_and_number_to_item[car]

            CarToWash.objects.filter(

            )

    def create_cars(self):
        for car in self.get_cars_to_create():
            item = self.__shift_id_and_number_to_item[car]

            with transaction.atomic():
                transferred_car = CarToWash(
                    shift_id=item['shift_id'],
                    car_wash_id=item['car_wash_id'],
                    car_number=item['car_number'],
                    class_type=item['class_type'],
                    wash_type=item['wash_type'],
                    windshield_washer_type=item['windshield_washer_type'],
                    windshield_washer_refilled_bottle_percentage=(
                        item['windshield_washer_refilled_bottle_percentage']
                    ),
                )
                transferred_car.full_clean()
                transferred_car.save()

                service_ids = [
                    service['id'] for service in item['additional_services']
                ]

                service_prices = CarWashServicePrice.objects.filter(
                    id__in=service_ids,
                )
                service_id_to_price = {
                    service_price.service_id: service_price.price
                    for service_price in service_prices
                }

                additional_services = []
                for service in item['additional_services']:
                    if (price := service['id']) not in service_id_to_price:
                        continue
                    additional_services.append(
                        CarToWashAdditionalService(
                            service_id=service['id'],
                            count=service['count'],
                            price=price,
                        )
                    )
                CarToWashAdditionalService.objects.batch_create(
                    additional_services
                )
