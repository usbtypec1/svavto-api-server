from dataclasses import dataclass
from uuid import UUID
from collections.abc import Iterable
from typing import TypedDict

from django.core.exceptions import ValidationError
from django.db import transaction

from shifts.models import CarToWash, CarToWashAdditionalService
from economics.models import StaffServicePrice
from shifts.exceptions import (
    StaffServicePriceNotFoundError,
    CarAlreadyWashedOnShiftError,
)
from shifts.selectors import get_staff_current_shift
from shifts.services.cars_to_wash import get_car_wash_service_prices


def compute_car_transfer_price(
    *,
    class_type: str,
    wash_type: str,
    is_extra_shift: bool,
) -> int:
    if wash_type == CarToWash.WashType.URGENT:
        service_name = StaffServicePrice.ServiceType.URGENT_CAR_WASH
    else:
        if is_extra_shift:
            service_name = StaffServicePrice.ServiceType.CAR_TRANSPORTER_EXTRA_SHIFT
        else:
            car_class_type_to_service_name: dict[str, str] = {
                CarToWash.CarType.COMFORT: StaffServicePrice.ServiceType.COMFORT_CLASS_CAR_TRANSFER,
                CarToWash.CarType.BUSINESS: StaffServicePrice.ServiceType.BUSINESS_CLASS_CAR_TRANSFER,
                CarToWash.CarType.VAN: StaffServicePrice.ServiceType.VAN_TRANSFER,
            }
            service_name = car_class_type_to_service_name[class_type]

    try:
        staff_service_price = StaffServicePrice.objects.get(service=service_name)
    except StaffServicePrice.DoesNotExist:
        raise StaffServicePriceNotFoundError(f"Not found {service_name}")
    return staff_service_price.price


@dataclass(frozen=True, slots=True)
class TransferredCarAdditionalServiceDto:
    id: UUID
    count: int


@dataclass(frozen=True, slots=True)
class TransferredCarCreateResultDto:
    id: int
    shift_id: int
    number: str
    class_type: str
    wash_type: str
    windshield_washer_type: str
    windshield_washer_refilled_bottle_percentage: int
    car_wash_id: int
    additional_services: list[TransferredCarAdditionalServiceDto]


def map_create_result_to_dto(
    transferred_car: CarToWash,
    additional_services: Iterable[CarToWashAdditionalService],
) -> TransferredCarCreateResultDto:
    additional_services_dto = [
        TransferredCarAdditionalServiceDto(
            id=service.service_id,
            count=service.count,
        )
        for service in additional_services
    ]
    return TransferredCarCreateResultDto(
        id=transferred_car.id,
        shift_id=transferred_car.shift_id,
        number=transferred_car.number,
        class_type=transferred_car.car_class,
        wash_type=transferred_car.wash_type,
        windshield_washer_type=transferred_car.windshield_washer_type,
        windshield_washer_refilled_bottle_percentage=(
            transferred_car.windshield_washer_refilled_bottle_percentage
        ),
        car_wash_id=transferred_car.car_wash_id,
        additional_services=additional_services_dto,
    )


class AdditionalService(TypedDict):
    id: UUID
    count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferredCarCreateUseCase:
    staff_id: int
    number: str
    car_class: str
    wash_type: str
    windshield_washer_type: str
    windshield_washer_refilled_bottle_percentage: int
    additional_services: list[AdditionalService]

    @transaction.atomic
    def execute(self) -> TransferredCarCreateResultDto:
        shift = get_staff_current_shift(self.staff_id)
        transfer_price = compute_car_transfer_price(
            class_type=self.car_class,
            wash_type=self.wash_type,
            is_extra_shift=shift.is_extra,
        )
        car_wash = shift.car_wash
        transferred_car = CarToWash(
            shift_id=shift.id,
            number=self.number.lower(),
            car_class=self.car_class,
            wash_type=self.wash_type,
            windshield_washer_type=self.windshield_washer_type,
            windshield_washer_refilled_bottle_percentage=(
                self.windshield_washer_refilled_bottle_percentage
            ),
            transfer_price=transfer_price,
            car_wash=car_wash,
            comfort_class_car_washing_price=car_wash.comfort_class_car_washing_price,
            business_class_car_washing_price=car_wash.business_class_car_washing_price,
            van_washing_price=car_wash.van_washing_price,
            windshield_washer_price_per_bottle=car_wash.windshield_washer_price_per_bottle,
        )
        try:
            transferred_car.full_clean()
            transferred_car.save()
        except ValidationError:
            raise CarAlreadyWashedOnShiftError

        service_ids = [service["id"] for service in self.additional_services]
        service_id_to_price = get_car_wash_service_prices(
            car_wash_id=car_wash.id,
            car_wash_service_ids=service_ids,
        )
        CarToWashAdditionalService.objects.filter(car=transferred_car).delete()
        if self.additional_services:
            services = [
                CarToWashAdditionalService(
                    car=transferred_car,
                    service_id=service["id"],
                    count=service["count"],
                    price=service_id_to_price[service["id"]],
                )
                for service in self.additional_services
            ]
            services = CarToWashAdditionalService.objects.bulk_create(services)
        else:
            services = []

        return map_create_result_to_dto(transferred_car, services)
