import datetime
from dataclasses import dataclass
from uuid import UUID

from shifts.exceptions import CarToWashNotFoundError
from shifts.models import CarToWash, CarToWashAdditionalService


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferredCarAdditionService:
    id: UUID
    name: str
    count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferredCarRetrieveResponseData:
    id: int
    staff_id: int
    staff_full_name: str
    shift_id: int
    shift_date: datetime.date
    number: str
    class_type: str
    wash_type: str
    car_wash_id: int
    car_wash_name: str
    windshield_washer_refilled_bottle_percentage: int
    additional_services: list[TransferredCarAdditionService]
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferredCarRetrieveInteractor:
    transferred_car_id: int

    def execute(self) -> TransferredCarRetrieveResponseData:
        try:
            transferred_car = (
                CarToWash.objects
                .select_related('shift__staff', 'car_wash')
                .only(
                    'id',
                    'number',
                    'shift__staff_id',
                    'car_class',
                    'wash_type',
                    'car_wash_id',
                    'car_wash__name',
                    'windshield_washer_refilled_bottle_percentage',
                    'additional_services',
                    'created_at',
                )
                .get(id=self.transferred_car_id)
            )
        except CarToWash.DoesNotExist:
            raise CarToWashNotFoundError(
                car_to_wash_id=self.transferred_car_id,
            )

        additional_services = (
            CarToWashAdditionalService.objects
            .select_related('service')
            .filter(car=transferred_car)
            .only('car_id', 'service_id', 'service__name', 'count')
        )

        return TransferredCarRetrieveResponseData(
            id=transferred_car.id,
            staff_id=transferred_car.shift.staff_id,
            staff_full_name=transferred_car.shift.staff.full_name,
            shift_id=transferred_car.shift_id,
            shift_date=transferred_car.shift.date,
            number=transferred_car.number,
            class_type=transferred_car.car_class,
            wash_type=transferred_car.wash_type,
            car_wash_id=transferred_car.car_wash_id,
            car_wash_name=transferred_car.car_wash.name,
            windshield_washer_refilled_bottle_percentage=(
                transferred_car.windshield_washer_refilled_bottle_percentage
            ),
            additional_services=[
                TransferredCarAdditionService(
                    id=service.service_id,
                    name=service.service.name,
                    count=service.count,
                )
                for service in additional_services
            ],
            created_at=transferred_car.created_at,
        )
