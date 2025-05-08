from dataclasses import dataclass
from typing import Protocol

from economics.models import (
    CarTransporterAndWasherServicePrices,
    CarTransporterServicePrices,
)
from shifts.models import TransferredCar
from staff.models import StaffType


class HasComfortBusinessVanCarTransferPrices(Protocol):
    comfort_class_car_transfer: int
    business_class_car_transfer: int
    van_transfer: int


def calculate_car_transfer_prices_by_class_type(
        class_type: str,
        prices: HasComfortBusinessVanCarTransferPrices
) -> int:
    car_class_type_to_service_name: dict[str, int] = {
        TransferredCar.CarType.COMFORT: prices.comfort_class_car_transfer,
        TransferredCar.CarType.BUSINESS:
            prices.business_class_car_transfer,
        TransferredCar.CarType.VAN: prices.van_transfer,
    }
    return car_class_type_to_service_name[class_type]


@dataclass(frozen=True, slots=True, kw_only=True)
class CarTransporterAndWasherTransferPriceCalculator:
    class_type: str
    wash_type: str

    def calculate(self) -> int:
        prices = CarTransporterAndWasherServicePrices.get()
        if self.wash_type == TransferredCar.WashType.URGENT:
            return prices.urgent_car_transfer
        return calculate_car_transfer_prices_by_class_type(
            class_type=self.class_type,
            prices=prices,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CarTransporterTransferPriceCalculator:
    class_type: str
    wash_type: str
    is_extra_shift: bool

    def calculate(self) -> int:
        prices = CarTransporterServicePrices.get()
        if self.wash_type == TransferredCar.WashType.URGENT:
            return prices.urgent_car_transfer

        if self.is_extra_shift:
            return prices.extra_shift

        return calculate_car_transfer_prices_by_class_type(
            class_type=self.class_type,
            prices=prices,
        )


def calculate_car_transfer_price(
        class_type: str,
        wash_type: str,
        is_extra_shift: bool,
        staff_type: int,
):
    if staff_type == StaffType.CAR_TRANSPORTER:
        calculator = CarTransporterTransferPriceCalculator(
            class_type=class_type,
            wash_type=wash_type,
            is_extra_shift=is_extra_shift,
        )
    else:
        calculator = CarTransporterAndWasherTransferPriceCalculator(
            class_type=class_type,
            wash_type=wash_type,
        )
    return calculator.calculate()
