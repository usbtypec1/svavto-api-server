from dataclasses import dataclass

from django.db import transaction

from shifts.models import CarToWash, CarToWashAdditionalService
from shifts.services.cars_to_wash import get_car_wash_service_prices


@dataclass(frozen=True, slots=True, kw_only=True)
class TransferredCarUpdateUseCase:
    """
    Use case to update all fields of CarToWash model.

    Args:
        car_id: The ID of the car to wash.
        number: The car's number.
        car_wash_id: The ID of the car wash.
        class_type: The car class.
        wash_type: The type of wash.
        windshield_washer_refilled_bottle_percentage: Windshield washer
        refill percentage.
        additional_services: List of additional services.
    """

    car_id: int
    number: str | None = None
    car_wash_id: int | None = None
    class_type: str | None = None
    wash_type: str | None = None
    windshield_washer_type: str | None = None
    windshield_washer_refilled_bottle_percentage: int | None = None
    additional_services: list[dict] | None = None

    @transaction.atomic
    def execute(self) -> list[CarToWashAdditionalService]:
        """
        Update all fields of CarToWash and its additional services.
        """
        transferred_car = CarToWash.objects.get(id=self.car_id)
        old_car_wash_id = transferred_car.car_wash_id

        if self.number is not None:
            transferred_car.number = self.number.lower()
        if self.car_wash_id is not None:
            transferred_car.car_wash_id = self.car_wash_id
        if self.class_type is not None:
            transferred_car.car_class = self.class_type
        if self.wash_type is not None:
            transferred_car.wash_type = self.wash_type
        if self.windshield_washer_refilled_bottle_percentage is not None:
            transferred_car.windshield_washer_refilled_bottle_percentage = (
                self.windshield_washer_refilled_bottle_percentage
            )
        if self.windshield_washer_type is not None:
            transferred_car.windshield_washer_type = self.windshield_washer_type
            if self.windshield_washer_type == CarToWash.WindshieldWasherType.WATER:
                transferred_car.windshield_washer_refilled_bottle_percentage = 0
        transferred_car.save()

        if self.additional_services is not None:
            service_ids = [service["id"] for service in self.additional_services]
            service_id_to_price = get_car_wash_service_prices(
                car_wash_id=old_car_wash_id,
                car_wash_service_ids=service_ids,
            )
            CarToWashAdditionalService.objects.filter(car_id=self.car_id).delete()
            if not self.additional_services:
                return []
            services = [
                CarToWashAdditionalService(
                    car_id=self.car_id,
                    service_id=service["id"],
                    count=service["count"],
                    price=service_id_to_price[service["id"]],
                )
                for service in self.additional_services
            ]
            return CarToWashAdditionalService.objects.bulk_create(services)
        return []
