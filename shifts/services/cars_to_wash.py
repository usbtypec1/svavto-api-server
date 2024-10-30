from django.db import transaction

from shifts.models import CarToWash, CarToWashAdditionalService, Shift


@transaction.atomic
def create_car_to_wash(
        *,
        shift: Shift,
        number: str,
        car_class: str,
        wash_type: str,
        windshield_washer_refilled_bottle_percentage: int,
        additional_services: list[dict],
):
    car_to_wash = CarToWash.objects.create(
        shift_id=shift.id,
        number=number,
        car_class=car_class,
        wash_type=wash_type,
        windshield_washer_refilled_bottle_percentage=(
            windshield_washer_refilled_bottle_percentage
        ),
        car_wash_id=shift.car_wash_id,
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
    CarToWashAdditionalService.objects.bulk_create(additional_services)
