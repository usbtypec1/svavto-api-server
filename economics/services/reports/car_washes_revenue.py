import collections
import datetime
from dataclasses import dataclass
from uuid import UUID

from django.db.models import Count, Q

from car_washes.models import CarWashServicePrice
from shifts.models import CarToWash, CarToWashAdditionalService

__all__ = ('ServiceProvidedByCarWash', 'CarWashesRevenueReportGenerator')


@dataclass(frozen=True, slots=True)
class ServiceProvidedByCarWash:
    id: UUID
    name: str
    price: int


class CarWashesRevenueReportGenerator:
    def __init__(
            self,
            *,
            car_wash_ids: int,
            from_date: datetime.date,
            to_date: datetime.date,
    ):
        self.__car_wash_ids = car_wash_ids
        self.__from_date = from_date
        self.__to_date = to_date

    def get_services_provided_by_car_wash(
            self,
    ) -> list[ServiceProvidedByCarWash]:
        car_wash_service_prices = (
            CarWashServicePrice.objects
            .filter(car_wash_id__in=self.__car_wash_ids)
            .values('service_id', 'price', 'service__name')
        )
        return [
            ServiceProvidedByCarWash(
                id=service['service_id'],
                name=service['service__name'],
                price=service['price'],
            )
            for service in car_wash_service_prices
        ]

    def compute_additional_services(
            self,
    ):
        additional_services = (
            CarToWashAdditionalService.objects.filter(
                car__shift__date__gte=self.__from_date,
                car__shift__date__lte=self.__to_date,
                car__car_wash_id__in=self.__car_wash_ids,
            )
            .select_related('service')
            .values('service_id', 'service__name', 'car__shift__date', 'count')
        )

        date_to_services = collections.defaultdict(list)
        for service in additional_services:
            date_to_services[service['car__shift__date']].append(service)

        result = []
        for date, services in date_to_services.items():
            services_grouped_by_date = []
            service_id_to_count = collections.defaultdict(int)
            for service in services:
                service_id_to_count[service['service_id']] += service['count']

            for service_id, count in service_id_to_count.items():
                services_grouped_by_date.append(
                    {
                        'id': service_id,
                        'count': count,
                    }
                )

            result.append(
                {
                    'date': date,
                    'services': services_grouped_by_date,
                }
            )
        return result

    def compute_cars_count(self):
        cars_to_wash = (
            CarToWash.objects.select_related('shift')
            .filter(
                shift__date__gte=self.__from_date,
                shift__date__lte=self.__to_date,
                car_wash_id__in=self.__car_wash_ids,
            )
            .values('shift__date')
            .annotate(
                planned_comfort_cars_washed_count=Count(
                    'id',
                    filter=Q(
                        car_class=CarToWash.CarType.COMFORT,
                        shift__is_extra=False,
                        wash_type=CarToWash.WashType.PLANNED,
                    ),
                ),
                planned_business_count=Count(
                    'id',
                    filter=Q(
                        car_class=CarToWash.CarType.BUSINESS,
                        shift__is_extra=False,
                        wash_type=CarToWash.WashType.PLANNED,
                    ),
                ),
                planned_van_count=Count(
                    'id',
                    filter=Q(
                        car_class=CarToWash.CarType.VAN,
                        shift__is_extra=False,
                        wash_type=CarToWash.WashType.PLANNED,
                    ),
                ),
                extra_count=Count(
                    'id',
                    filter=Q(shift__is_extra=True),
                ),
                urgent_count=Count(
                    'id',
                    filter=Q(
                        wash_type=CarToWash.WashType.URGENT,
                        shift__is_extra=False,
                    ),
                ),
            )
        )
        for car in cars_to_wash:
            car['date'] = car.pop('shift__date')
        return list(cars_to_wash)

    def get_cars_count_with_additional_services(
            self,
    ):
        cars_count = self.compute_cars_count()
        additional_services = self.compute_additional_services()
        date_to_additional_services = {
            additional_service['date']: additional_service['services']
            for additional_service in additional_services
        }

        return [
            {
                **cars_count_for_date,
                'additional_services': date_to_additional_services.get(
                    cars_count_for_date['date'],
                    [],
                ),
            }
            for cars_count_for_date in cars_count
        ]

    def generate_report(self) -> dict:
        return {
            'report_by_dates': self.get_cars_count_with_additional_services(),
            'car_wash_additional_services': (
                self.get_services_provided_by_car_wash()
            ),
        }
