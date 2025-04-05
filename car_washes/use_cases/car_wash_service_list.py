from collections.abc import Iterable
from dataclasses import dataclass

from car_washes.selectors import (
    CarWashServiceListItemDto,
    flatten_car_wash_services,
    get_all_car_wash_services,
    get_services_of_car_washes,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashServiceListUseCase:
    car_wash_ids: Iterable[int] | None

    def execute(self) -> list[CarWashServiceListItemDto]:
        if self.car_wash_ids is not None:
            car_wash_services = get_services_of_car_washes(self.car_wash_ids)
        else:
            car_wash_services = get_all_car_wash_services()
        return flatten_car_wash_services(car_wash_services)
