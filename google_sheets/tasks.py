from collections import defaultdict

from celery import shared_task
from django.db.models import QuerySet
from django.utils import timezone

from car_washes.models import CarWash
from google_sheets.services import create_google_sheets_client
from shifts.models import CarToWash

__all__ = ('sync_car_washes',)


@shared_task
def sync_car_washes() -> None:
    client = create_google_sheets_client()
    car_washes_spreadsheet = client.open_by_key(
        '1r5HLSw-F0jAVx1bTPeHKK3TuS0syzsdHUqIwaBXWnMM',
    )

    worksheets = car_washes_spreadsheet.worksheets()

    worksheet_titles = {worksheet.title for worksheet in worksheets}
    print(worksheet_titles)

    car_washes = CarWash.objects.all()

    for car_wash in car_washes:
        if car_wash.name not in worksheet_titles:
            # TODO если произошло добавление, нужно перезаписать формулы в
            #  листе "сумма"
            car_washes_spreadsheet.add_worksheet(
                title=car_wash.name,
                rows=10,
                cols=15,
            )

    car_washes = CarWash.objects.prefetch_related('carwashserviceprice_set')

    yesterday = timezone.now() - timezone.timedelta(days=1)

    for car_wash in car_washes:
        car_wash_service_prices = car_wash.carwashserviceprice_set.all()
        service_id_to_price = {
            service.id: service.price for service in car_wash_service_prices
        }

        cars_to_wash: QuerySet[CarToWash] = CarToWash.objects.filter(
            shift__date=yesterday
        ).prefetch_related('cartowashadditionalservice_set')

        car_class_type_to_count = defaultdict(int)

        for car in cars_to_wash:
            car_class_type_to_count[car.car_class] += 1

        for car in cars_to_wash:
            for additional_service in car.cartowashadditionalservice_set.all():
                if additional_service.name not in service_id_to_price:
                    print('Service not found')
                else:
                    service_price = service_id_to_price[additional_service.name]

        worksheet = car_washes_spreadsheet.worksheet(car_wash.name)
