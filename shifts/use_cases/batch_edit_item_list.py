import datetime
from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from shifts.models import CarToWash, CarToWashAdditionalService


@dataclass(frozen=True, slots=True, kw_only=True)
class AdditionalServiceDto:
    id: UUID
    name: str
    count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class CarDto:
    id: int
    number: str
    car_wash_id: int
    car_wash_name: str
    class_type: str
    wash_type: str
    windshield_washer_type: str
    windshield_washer_refilled_bottle_percentage: int
    additional_services: list[AdditionalServiceDto]


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftDto:
    id: int
    date: datetime.date
    staff_id: int
    staff_full_name: str
    cars: list[CarDto]


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchEditItemListUseCase:
    date: datetime.date
    staff_id: int | None

    def execute(self) -> list[ShiftDto]:
        cars = (
            CarToWash.objects
            .filter(shift__date=self.date)
            .select_related('shift__staff')
            .select_related('car_wash', 'shift')
            .order_by('shift_id', 'shift__date', 'shift__staff_id')
        )
        if self.staff_id is not None:
            cars = cars.filter(shift__staff_id=self.staff_id)

        additional_services = (
            CarToWashAdditionalService.objects
            .filter(car__in=cars)
            .select_related('service')
        )

        car_id_to_services: dict[int, list[AdditionalServiceDto]] = (
            defaultdict(list)
        )
        for service in additional_services:
            car_id_to_services[service.car_id].append(
                AdditionalServiceDto(
                    id=service.service.id,
                    name=service.service.name,
                    count=service.count
                )
            )

        shift_id_to_shift: dict[int, ShiftDto] = {}
        for car in cars:
            shift = car.shift
            if shift.id not in shift_id_to_shift:
                shift_id_to_shift[shift.id] = ShiftDto(
                    id=shift.id,
                    date=shift.date,
                    staff_id=shift.staff_id,
                    staff_full_name=shift.staff.full_name,
                    cars=[]
                )

            shift_id_to_shift[shift.id].cars.append(
                CarDto(
                    id=car.id,
                    number=car.number,
                    car_wash_id=car.car_wash.id if car.car_wash else None,
                    car_wash_name=car.car_wash.name if car.car_wash else "",
                    class_type=car.car_class,
                    wash_type=car.wash_type,
                    windshield_washer_type=car.windshield_washer_type,
                    windshield_washer_refilled_bottle_percentage=(
                        car.windshield_washer_refilled_bottle_percentage
                    ),
                    additional_services=car_id_to_services.get(car.id, [])
                )
            )

        return list(shift_id_to_shift.values())
