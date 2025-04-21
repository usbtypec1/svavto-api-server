import datetime
from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from shifts.models import CarToWash, CarToWashAdditionalService, Shift


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
        shifts = (
            Shift.objects
            .select_related('staff')
            .filter(date=self.date, staff__banned_at__isnull=True)
            .only('id', 'date', 'staff_id', 'staff__full_name')
        )
        if self.staff_id is not None:
            shifts = shifts.filter(staff_id=self.staff_id)

        cars = (
            CarToWash.objects
            .filter(shift__in=shifts)
            .select_related('car_wash')
            .order_by('shift_id', 'shift__date', 'shift__staff_id')
            .only(
                'id',
                'number',
                'car_wash_id',
                'car_wash__name',
                'car_class',
                'wash_type',
                'windshield_washer_type',
                'windshield_washer_refilled_bottle_percentage',
            )
        )
        if self.staff_id is not None:
            cars = cars.filter(shift__staff_id=self.staff_id)

        additional_services = (
            CarToWashAdditionalService.objects
            .filter(car__in=cars)
            .select_related('service')
            .only('car_id', 'service__id', 'service__name', 'count')
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

        shift_id_to_cars: dict[int, list[CarDto]] = defaultdict(list)
        for car in cars:
            shift_id_to_cars[car.shift_id].append(
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

        return [
            ShiftDto(
                id=shift.id,
                date=shift.date,
                staff_id=shift.staff_id,
                staff_full_name=shift.staff.full_name,
                cars=shift_id_to_cars[shift.id]
            )
            for shift in shifts
        ]
