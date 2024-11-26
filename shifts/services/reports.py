import datetime
from typing import List, TypedDict

from django.db.models import Count, Q, Sum

from economics.models import Penalty, Surcharge
from shifts.models import CarToWash, CarToWashAdditionalService


class StaffStats(TypedDict):
    surcharge_count: int
    surcharge_total: int
    penalty_count: int


class DailyStats(TypedDict):
    date: str
    cars_washed: int
    comfort_cars: int
    business_cars: int
    van_cars: int
    planned_washes: int
    urgent_washes: int
    additional_services: int
    total_additional_services_count: int
    windshield_refills: int


class PeriodStats(TypedDict):
    daily_stats: List[DailyStats]
    total_cars: int
    total_additional_services: int
    total_comfort_cars: int
    total_business_cars: int
    total_van_cars: int
    total_planned_washes: int
    total_urgent_washes: int


def get_detailed_period_report(
    staff_id: int, from_date: datetime.date, to_date: datetime.date
) -> dict:
    """
    Generate a detailed report of operations for the specified period.

    Args:
        staff_id: ID of the staff member
        from_date: Start date of the period (inclusive)
        to_date: End date of the period (inclusive)

    Returns:
        Detailed statistics broken down by day and totals for the period
    """
    # Base queryset for the period
    base_qs = CarToWash.objects.filter(
        shift__staff_id=staff_id,
        shift__date__gte=from_date,
        shift__date__lte=to_date,
        shift__finished_at__isnull=False,  # Only count completed shifts
    )

    # Get daily statistics
    daily_stats = (
        base_qs.values('shift__date')
        .annotate(
            cars_washed=Count('id'),
            comfort_cars=Count(
                'id',
                filter=Q(car_class=CarToWash.CarType.COMFORT),
            ),
            business_cars=Count(
                'id',
                filter=Q(car_class=CarToWash.CarType.BUSINESS),
            ),
            van_cars=Count(
                'id',
                filter=Q(car_class=CarToWash.CarType.VAN),
            ),
            planned_washes=Count(
                'id',
                filter=Q(wash_type=CarToWash.WashType.PLANNED),
            ),
            urgent_washes=Count(
                'id',
                filter=Q(wash_type=CarToWash.WashType.URGENT),
            ),
            windshield_refills=Sum(
                'windshield_washer_refilled_bottle_percentage'
            ),
        )
        .order_by('shift__date')
    )

    # Get additional services details
    additional_services_count = CarToWashAdditionalService.objects.filter(
        car__in=base_qs
    ).count()

    # Calculate period totals
    period_totals = base_qs.aggregate(
        cars_washed=Count('id'),
        additional_services_count=Count(
            'cartowashadditionalservice', distinct=True
        ),
        comfort_cars=Count(
            'id',
            filter=Q(car_class=CarToWash.CarType.COMFORT),
        ),
        business_cars=Count(
            'id',
            filter=Q(car_class=CarToWash.CarType.BUSINESS),
        ),
        van_cars=Count(
            'id',
            filter=Q(car_class=CarToWash.CarType.VAN),
        ),
        planned_washes=Count(
            'id',
            filter=Q(wash_type=CarToWash.WashType.PLANNED),
        ),
        urgent_washes=Count(
            'id',
            filter=Q(wash_type=CarToWash.WashType.URGENT),
        ),
    )

    # Clean period totals to handle None values
    cleaned_period_totals = {
        key: value if value is not None else 0
        for key, value in period_totals.items()
    }

    return {
        'daily_stats': [
            {
                'date': stat['shift__date'].isoformat(),
                'cars_washed': stat.get('cars_washed', 0),
                'comfort_cars': stat.get('comfort_cars', 0),
                'business_cars': stat.get('business_cars', 0),
                'van_cars': stat.get('van_cars', 0),
                'planned_washes': stat.get('planned_washes', 0),
                'urgent_washes': stat.get('urgent_washes', 0),
                'additional_services_count': stat.get(
                    'additional_services_count', 0
                ),
                'windshield_refills': stat.get('windshield_refills', 0),
            }
            for stat in daily_stats
        ],
        'period_totals': {
            **cleaned_period_totals,
            'shifts_count': len(daily_stats),
            'additional_services_count': additional_services_count,
        },
    }


def get_financial_statistics(
    staff_id: int, from_date: datetime.date, to_date: datetime.date
) -> StaffStats:
    """
    Calculate statistics for a staff member within a specified date range.

    Args:
        staff_id: ID of the staff member
        from_date: Start date of the period (inclusive)
        to_date: End date of the period (inclusive)

    Returns:
        Dictionary containing counts and sums of surcharges and penalties
    """
    # Get surcharge statistics
    surcharge_stats = Surcharge.objects.filter(
        staff_id=staff_id,
        created_at__date__gte=from_date,
        created_at__date__lte=to_date,
    ).aggregate(surcharge_count=Count('id'), surcharge_total=Sum('amount'))

    # Get penalty count
    penalty_count = Penalty.objects.filter(
        staff_id=staff_id,
        created_at__date__gte=from_date,
        created_at__date__lte=to_date,
    ).count()

    return {
        'surcharge_count': surcharge_stats.get('surcharge_count', 0),
        'surcharge_total': surcharge_stats.get('surcharge_total', 0),
        'penalty_count': penalty_count,
    }
