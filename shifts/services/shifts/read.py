from django.db.models import QuerySet

from core.services import get_current_shift_date
from shifts.models import Shift


def get_staff_ids_with_not_started_shifts_for_today() -> set[int]:
    return set(
        Shift.objects
        .filter(
            date=get_current_shift_date(),
            started_at__isnull=True,
            rejected_at__isnull=True,
        )
        .values_list('staff_id', flat=True)
    )


def get_shifts_by_staff_id(
        *,
        staff_id: int,
        month: int | None,
        year: int | None,
) -> QuerySet[Shift]:
    shifts = Shift.objects.select_related('car_wash').filter(staff_id=staff_id)
    if month is not None:
        shifts = shifts.filter(date__month=month)
    if year is not None:
        shifts = shifts.filter(date__year=year)
    return shifts
