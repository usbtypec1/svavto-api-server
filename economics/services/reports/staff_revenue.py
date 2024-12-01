import collections
import datetime

from django.db.models import Count, Q, Sum

from economics.models import Penalty, Surcharge
from shifts.models import CarToWash
from staff.models import Staff

__all__ = (
    'merge_staff_statistics',
    'StaffRevenueReportGenerator',
)


def merge_staff_statistics(
        staff_id: int,
        staff_id_to_penalty_amount: dict[int, int],
        staff_id_to_surcharge_amount: dict[int, int],
        staff_id_to_cars: dict[int, dict],
) -> dict:
    penalty_amount: int = staff_id_to_penalty_amount.get(staff_id, 0)
    surcharge_amount: int = staff_id_to_surcharge_amount.get(staff_id, 0)
    cars_statistics = staff_id_to_cars.get(staff_id, {})
    keys = (
        'planned_comfort_cars_washed_count',
        'planned_business_cars_washed_count',
        'planned_business_cars_washed_count',
        'planned_vans_washed_count',
        'urgent_cars_washed_count',
        'total_cost',
    )
    statistics = {key: cars_statistics.get(key, 0) for key in keys}
    return {
        'staff_id': staff_id,
        'penalty_amount': penalty_amount,
        'surcharge_amount': surcharge_amount,
        'is_extra_shift': cars_statistics.get('is_extra', False),
    } | statistics


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
            .values('shift__date', 'shift__staff_id', 'shift__is_extra')
            .annotate(
                total_cost=Sum('transfer_price', default=0),
                planned_comfort_cars_washed_count=Count(
                    'transfer_price',
                    filter=Q(
                        car_class=CarToWash.CarType.COMFORT,
                        wash_type=CarToWash.WashType.PLANNED,
                    ),
                ),

                planned_business_cars_washed_count=Count(
                    'transfer_price',
                    filter=Q(
                        car_class=CarToWash.CarType.BUSINESS,
                        wash_type=CarToWash.WashType.PLANNED,
                    ),
                ),
                planned_vans_washed_count=Count(
                    'transfer_price',
                    filter=Q(
                        car_class=CarToWash.CarType.VAN,
                        shift__is_extra=False,
                        wash_type=CarToWash.WashType.PLANNED,
                    ),
                ),
                urgent_cars_washed_count=Count(
                    'transfer_price',
                    filter=Q(
                        wash_type=CarToWash.WashType.URGENT,
                        shift__is_extra=False,
                    ),
                ),
            )
        )

        date_to_cars: dict[datetime.date, dict[int, dict]] = (
            collections.defaultdict(dict)
        )
        for car in cars_to_wash:
            date = car.pop('shift__date')
            staff_id: int = car.pop('shift__staff_id')
            car['is_extra'] = car.pop('shift__is_extra')
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
