from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from uuid import UUID

from django.db import transaction
from django.db.models import Q, QuerySet
from typing_extensions import TypedDict

from car_washes.models import CarWash, CarWashServicePrice
from shifts.models import CarToWash, CarToWashAdditionalService, Shift
from shifts.services.transferred_cars.create import \
    calculate_car_transfer_price


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
        .prefetch_related('additional_services__service')
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

    def get_all_service_ids(self) -> set[UUID]:
        return {
            service['id']
            for item in self.__items
            for service in item['additional_services']
        }

    def get_service_id_to_price(self) -> dict[UUID, int]:
        service_prices = CarWashServicePrice.objects.filter(
            service_id__in=self.get_all_service_ids(),
        ).values('price', 'service_id')
        return {
            service_price['service_id']: service_price['price']
            for service_price in service_prices
        }

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
        if filter_q:
            CarToWash.objects.filter(filter_q).delete()

    @transaction.atomic
    def update_cars(self):
        transferred_cars_query = Q()
        for shift_id, car_number in self.get_cars_to_update():
            transferred_cars_query |= Q(
                shift_id=shift_id,
                number=car_number,
            )
        if not transferred_cars_query:
            return

        service_id_to_price = self.get_service_id_to_price()

        transferred_cars = CarToWash.objects.filter(transferred_cars_query)

        for transferred_car in transferred_cars:
            item = self.__shift_id_and_number_to_item[
                (transferred_car.shift_id, transferred_car.number)
            ]
            transferred_car.car_wash_id = item['car_wash_id']
            transferred_car.car_class = item['class_type']
            transferred_car.wash_type = item['wash_type']
            transferred_car.windshield_washer_type = item[
                'windshield_washer_type']
            transferred_car.windshield_washer_refilled_bottle_percentage = (
                item['windshield_washer_refilled_bottle_percentage']
            )

        CarToWash.objects.bulk_update(
            transferred_cars,
            fields=(
                'car_wash_id',
                'car_class',
                'wash_type',
                'windshield_washer_type',
                'windshield_washer_refilled_bottle_percentage',
            ),
        )

        delete_q = Q()
        for transferred_car in transferred_cars:
            delete_q |= Q(
                car_id=transferred_car.id,
            )
        if delete_q:
            CarToWashAdditionalService.objects.filter(delete_q).delete()
            

        additional_services = []
        for transferred_car in transferred_cars:
            item = self.__shift_id_and_number_to_item[
                (transferred_car.shift_id, transferred_car.number)
            ]
            for service in item['additional_services']:
                if service['id'] not in service_id_to_price:
                    continue
                price = service_id_to_price[service['id']]
                if service['count'] < 1:
                    continue
                additional_services.append(
                    CarToWashAdditionalService(
                        car_id=transferred_car.id,
                        service_id=service['id'],
                        count=service['count'],
                        price=price,
                    )
                )
        if additional_services:
            CarToWashAdditionalService.objects.bulk_create(
                additional_services
            )

    @lru_cache(maxsize=100)
    def get_car_wash_by_id(self, car_wash_id: int) -> CarWash | None:
        return CarWash.objects.filter(id=car_wash_id).first()

    @transaction.atomic
    def create_cars(self):
        cars_to_create = self.get_cars_to_create()
        shift_ids = {
            self.__shift_id_and_number_to_item[car]['shift_id']
            for car in cars_to_create
        }
        shift_id_to_staff_type = {
            shift.id: shift.staff.type
            for shift in
            Shift.objects.filter(id__in=shift_ids).select_related('staff')
        }

        service_id_to_price = self.get_service_id_to_price()

        transferred_cars = []

        for car in cars_to_create:
            item = self.__shift_id_and_number_to_item[car]
            shift_id = item['shift_id']
            car_wash = self.get_car_wash_by_id(item['car_wash_id'])
            if car_wash is None:
                continue
            transfer_price = calculate_car_transfer_price(
                class_type=item['class_type'],
                wash_type=item['wash_type'],
                is_extra_shift=shift_id in self.__extra_shift_ids,
                staff_type=shift_id_to_staff_type[shift_id]
            )
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
            transferred_cars.append(transferred_car)

        CarToWash.objects.bulk_create(transferred_cars)

        additional_services = []
        for transferred_car in transferred_cars:
            item = self.__shift_id_and_number_to_item[
                (transferred_car.shift_id, transferred_car.number)
            ]
            for service in item['additional_services']:
                if service['id'] not in service_id_to_price:
                    continue
                if service['count'] < 1:
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
        if additional_services:
            CarToWashAdditionalService.objects.bulk_create(
                additional_services
            )
