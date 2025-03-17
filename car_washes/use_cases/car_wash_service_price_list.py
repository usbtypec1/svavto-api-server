import datetime
from dataclasses import dataclass
from uuid import UUID

from car_washes.models import CarWashServicePrice, CarWash
from car_washes.exceptions import CarWashNotFoundError


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashServicePriceListItemDto:
    id: UUID
    name: str
    price: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashServicePriceListDto:
    car_wash_id: int
    car_wash_name: str
    services: list[CarWashServicePriceListItemDto]


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashServicePriceListUseCase:
    car_wash_id: int

    def execute(self) -> CarWashServicePriceListDto:
        try:
            car_wash = CarWash.objects.only("id", "name").get(id=self.car_wash_id)
        except CarWash.DoesNotExist:
            raise CarWashNotFoundError

        service_prices = (
            CarWashServicePrice.objects.filter(car_wash=car_wash)
            .select_related("service")
            .only("price", "created_at", "updated_at", "service__id", "service__name")
        )

        services = [
            CarWashServicePriceListItemDto(
                id=service_price.service.id,
                name=service_price.service.name,
                price=service_price.price,
                created_at=service_price.created_at,
                updated_at=service_price.updated_at,
            )
            for service_price in service_prices
        ]
        return CarWashServicePriceListDto(
            car_wash_id=car_wash.id,
            car_wash_name=car_wash.name,
            services=services,
        )
