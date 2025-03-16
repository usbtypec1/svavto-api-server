import datetime
from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from shifts.models import CarToWash, CarToWashAdditionalService
from shifts.selectors import get_shift_by_id


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferredCarAdditionService:
    id: UUID
    name: str
    count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferredCarListItem:
    id: int
    number: str
    class_type: str
    wash_type: str
    car_wash_id: int
    car_wash_name: str
    windshield_washer_refilled_bottle_percentage: int
    additional_services: list[TransferredCarAdditionService]
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferredCarListResponseData:
    staff_id: int
    staff_full_name: str
    shift_id: int
    shift_date: datetime.date
    transferred_cars: list[TransferredCarListItem]


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferredCarListInteractor:
    shift_id: int

    def execute(self) -> TransferredCarListResponseData:
        shift = get_shift_by_id(self.shift_id)

        transferred_cars = (
            CarToWash.objects.select_related("shift__staff", "car_wash")
            .filter(shift_id=self.shift_id)
            .only(
                "id",
                "number",
                "shift__staff_id",
                "car_class",
                "wash_type",
                "car_wash_id",
                "car_wash__name",
                "windshield_washer_refilled_bottle_percentage",
                "additional_services",
                "created_at",
            )
        )
        additional_services = (
            CarToWashAdditionalService.objects.select_related("service")
            .filter(car__shift_id=self.shift_id)
            .only("car_id", "service_id", "service__name", "count")
        )

        transferred_car_id_to_services = defaultdict(list)
        for additional_service in additional_services:
            transferred_car_id_to_services[additional_service.car_id].append(
                TransferredCarAdditionService(
                    id=additional_service.service_id,
                    name=additional_service.service.name,
                    count=additional_service.count,
                )
            )

        transferred_car_dtos = []
        for car in transferred_cars:
            car_list_item = TransferredCarListItem(
                id=car.id,
                number=car.number,
                class_type=car.car_class,
                wash_type=car.wash_type,
                car_wash_id=car.car_wash_id,
                car_wash_name=car.car_wash.name,
                windshield_washer_refilled_bottle_percentage=(
                    car.windshield_washer_refilled_bottle_percentage
                ),
                additional_services=transferred_car_id_to_services[car.id],
                created_at=car.created_at,
            )
            transferred_car_dtos.append(car_list_item)

        return TransferredCarListResponseData(
            staff_id=shift.staff.id,
            staff_full_name=shift.staff.full_name,
            shift_id=shift.id,
            shift_date=shift.date,
            transferred_cars=transferred_car_dtos,
        )
