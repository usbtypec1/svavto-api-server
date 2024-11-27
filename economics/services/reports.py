import collections
import datetime
from collections.abc import Iterable
from typing import TypedDict, TypeVar
from uuid import UUID

from django.db.models import Count, Q, Sum

from car_washes.models import CarWashServicePrice
from economics.models import Penalty, Surcharge
from shifts.models import CarToWash, CarToWashAdditionalService
from staff.models import Staff

__all__ = ('ServiceCostsReportGenerator',)


class ServiceProvidedByCarWash(TypedDict):
    id: UUID
    name: str
    price: int


def merge_staff_statistics(
    staff_id: int,
    staff_id_to_penalty_amount: dict[int, int],
    staff_id_to_surcharge_amount: dict[int, int],
    staff_id_to_cars: dict[int, dict],
) -> dict:
    penalty_amount: int = staff_id_to_penalty_amount.get(staff_id, 0)
    surcharge_amount: int = staff_id_to_surcharge_amount.get(staff_id, 0)
    planned_comfort_cars_washing_cost: int = staff_id_to_cars.get(staff_id, {}).get('planned_comfort', 0)
    planned_business_cars_washing_cost: int = staff_id_to_cars.get(staff_id, {}).get('planned_business', 0)
    planned_vans_washing_cost: int = staff_id_to_cars.get(staff_id, {}).get('planned_van', 0)
    extra_shift_washing_cost: int = staff_id_to_cars.get(staff_id, {}).get('extra', 0)
    urgent_washing_cost: int = staff_id_to_cars.get(staff_id, {}).get('urgent', 0)
    return {
        'staff_id': staff_id,
        'penalty_amount': penalty_amount,
        'surcharge_amount': surcharge_amount,
        'planned_comfort_cars_washing_cost': planned_comfort_cars_washing_cost,
        'planned_business_cars_washing_cost': planned_business_cars_washing_cost,
        'planned_vans_washing_cost': planned_vans_washing_cost,
        'extra_shift_washing_cost': extra_shift_washing_cost,
        'urgent_washing_cost': urgent_washing_cost,
    }


class ServiceCostsReportGenerator:
    def __init__(
        self,
        *,
        car_wash_id: int,
        from_date: datetime.date,
        to_date: datetime.date,
    ):
        self.__car_wash_id = car_wash_id
        self.__from_date = from_date
        self.__to_date = to_date

    def get_services_provided_by_car_wash(
        self,
    ) -> list[ServiceProvidedByCarWash]:
        car_wash_service_prices = CarWashServicePrice.objects.filter(
            car_wash_id=self.__car_wash_id
        ).values('service_id', 'price', 'service__name')
        return [
            {
                'id': service['service_id'],
                'name': service['service__name'],
                'price': service['price'],
            }
            for service in car_wash_service_prices
        ]

    def compute_additional_services(
        self,
    ):
        additional_services = (
            CarToWashAdditionalService.objects.filter(
                car__shift__date__gte=self.__from_date,
                car__shift__date__lte=self.__to_date,
                car__car_wash_id=self.__car_wash_id,
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
                car_wash_id=self.__car_wash_id,
            )
            .values('shift__date')
            .annotate(
                planned_comfort_count=Count(
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

    def get_additional_service_prices(
        self,
    ):
        car_wash_service_prices = CarWashServicePrice.objects.filter(
            car_wash_id=self.__car_wash_id
        ).values('service_id', 'price')
        return [
            {
                'id': service['service_id'],
                'price': service['price'],
            }
            for service in car_wash_service_prices
        ]

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


class StaffRevenueReportGenerator:
    def __init__(
        self,
        *,
        from_date: datetime.date,
        to_date: datetime.date,
    ):
        self.__from_date = from_date
        self.__to_date = to_date

    def get_cars(self) -> dict[datetime.date, dict[int, dict]]:
        cars_to_wash = (
            CarToWash.objects.select_related('shift')
            .filter(
                shift__date__gte=self.__from_date,
                shift__date__lte=self.__to_date,
            )
            .values('shift__date', 'shift__staff_id')
            .annotate(
                planned_comfort=Sum(
                    'transfer_price',
                    filter=Q(
                        car_class=CarToWash.CarType.COMFORT,
                        shift__is_extra=False,
                        wash_type=CarToWash.WashType.PLANNED,
                    ),
                    default=0,
                ),
                planned_business=Sum(
                    'transfer_price',
                    filter=Q(
                        car_class=CarToWash.CarType.BUSINESS,
                        shift__is_extra=False,
                        wash_type=CarToWash.WashType.PLANNED,
                    ),
                    default=0,
                ),
                planned_van=Sum(
                    'transfer_price',
                    filter=Q(
                        car_class=CarToWash.CarType.VAN,
                        shift__is_extra=False,
                        wash_type=CarToWash.WashType.PLANNED,
                    ),
                    default=0,
                ),
                extra=Sum(
                    'transfer_price',
                    filter=Q(shift__is_extra=True),
                    default=0,
                ),
                urgent=Sum(
                    'transfer_price',
                    filter=Q(
                        wash_type=CarToWash.WashType.URGENT,
                        shift__is_extra=False,
                    ),
                    default=0,
                ),
            )
        )

        date_to_cars: dict[datetime.date, dict[int, dict]] = (
            collections.defaultdict(dict)
        )
        for car in cars_to_wash:
            date = car.pop('shift__date')
            staff_id: int = car.pop('shift__staff_id')
            date_to_cars[date][staff_id] = car

        return dict(date_to_cars)

    def get_penalties(self) -> dict[datetime.date, dict[int, int]]:
        penalties = (
            Penalty.objects.filter(
                created_at__date__gte=self.__from_date,
                created_at__date__lte=self.__to_date,
            )
            .values('staff_id', 'created_at__date')
            .annotate(
                total_amount=Sum('amount'),
            )
        )
        date_to_penalties: dict[datetime.date, dict[int, int]] = (
            collections.defaultdict(dict)
        )
        for penalty in penalties:
            date: datetime.date = penalty['created_at__date']
            staff_id: int = penalty['staff_id']
            date_to_penalties[date][staff_id] = penalty['total_amount']
        return dict(date_to_penalties)

    def get_staff(self) -> tuple[dict, ...]:
        return tuple(
            Staff.objects.values(
                'id',
                'full_name',
                'car_sharing_phone_number',
                'console_phone_number',
            ).order_by('full_name')
        )

    def get_surcharges(self) -> dict[datetime.date, dict[int, int]]:
        surcharges = (
            Surcharge.objects.filter(
                created_at__date__gte=self.__from_date,
                created_at__date__lte=self.__to_date,
            )
            .values('staff_id', 'created_at__date')
            .annotate(
                total_amount=Sum('amount'),
            )
        )
        date_to_surcharges = collections.defaultdict(dict)
        for surcharge in surcharges:
            date: datetime.date = surcharge['created_at__date']
            staff_id: int = surcharge['staff_id']
            date_to_surcharges[date][staff_id] = surcharge['total_amount']
        return dict(date_to_surcharges)

    def get_merged_statistics(self) -> list[dict]:
        penalties_by_dates = self.get_penalties()
        surcharges_by_dates = self.get_surcharges()

        cars = self.get_cars()

        all_dates = sorted(
            set(penalties_by_dates) | set(surcharges_by_dates) | set(cars)
        )

        result = []
        for date in all_dates:
            staff_id_to_penalty_amount = penalties_by_dates.get(date, {})
            staff_id_to_surcharge_amount = surcharges_by_dates.get(date, {})
            staff_id_to_cars = cars.get(date, {})

            staff_ids = set(staff_id_to_penalty_amount) | set(
                staff_id_to_surcharge_amount
            )

            staff_statistics: list[dict] = [
                merge_staff_statistics(
                    staff_id=staff_id,
                    staff_id_to_penalty_amount=staff_id_to_penalty_amount,
                    staff_id_to_surcharge_amount=staff_id_to_surcharge_amount,
                    staff_id_to_cars=staff_id_to_cars,
                )
                for staff_id in staff_ids
            ]
            result.append({'date': date, 'statistics': staff_statistics})

        return result

    def generate_report(self) -> dict:
        staff_list = self.get_staff()
        staff_revenue = self.get_merged_statistics()
        return {'staff_revenue': staff_revenue, 'staff_list': staff_list}
