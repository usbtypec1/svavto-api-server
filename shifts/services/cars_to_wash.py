from django.db import transaction

from shifts.models import CarToWash, CarToWashAdditionalService


@transaction.atomic
def create_car_to_wash(
        *,
        shift_id: int,
        number: str,
        car_class: str,
        wash_type: str,
        windshield_washer_refilled_bottle_percentage: int,
        additional_services: list[dict],
):
    car_to_wash = CarToWash.objects.create(
        shift_id=shift_id,
        number=number,
        car_class=car_class,
        wash_type=wash_type,
        windshield_washer_refilled_bottle_percentage=(
            windshield_washer_refilled_bottle_percentage
        )
    )

    additional_services = [
        CarToWashAdditionalService(
            car=car_to_wash,
            name=service['name'],
            count=service['count'],
        )
        for service in additional_services
    ]
    CarToWashAdditionalService.objects.bulk_create(additional_services)


@transaction.atomic
def update_car_to_wash(
        *,
        car_id: int,
        additional_services: list[dict],
):
    additional_services = [
        CarToWashAdditionalService(
            car_id=car_id,
            name=service['name'],
            count=service['count'],
        )
        for service in additional_services
    ]
    CarToWashAdditionalService.objects.filter(car_id=car_id).delete()
    CarToWash.objects.bulk_create(additional_services)
