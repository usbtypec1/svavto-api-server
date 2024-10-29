from django.db import IntegrityError, transaction
from django.utils import timezone

from staff.exceptions import (
    StaffAlreadyExistsError,
    StaffNotFoundError,
)
from staff.models import Staff, StaffAvailableDate

__all__ = ('create_staff', 'update_staff', 'update_staff_shift_schedule')


def create_staff(
        *,
        staff_id: int,
        full_name: str,
        car_sharing_phone_number: str,
        console_phone_number: str,
) -> Staff:
    try:
        return Staff.objects.create(
            id=staff_id,
            full_name=full_name,
            car_sharing_phone_number=car_sharing_phone_number,
            console_phone_number=console_phone_number
        )
    except IntegrityError:
        raise StaffAlreadyExistsError


def update_staff(
        *,
        staff_id: int,
        is_banned: bool,
) -> None:
    banned_at = timezone.now() if is_banned else None
    is_updated = (
        Staff.objects
        .filter(id=staff_id)
        .update(banned_at=banned_at)
    )
    if not is_updated:
        raise StaffNotFoundError


@transaction.atomic
def update_staff_shift_schedule(
        *,
        staff_id: int,
        years_and_months: list[dict],
) -> None:
    StaffAvailableDate.objects.filter(staff_id=staff_id).delete()
    available_dates = [
        StaffAvailableDate(
            staff_id=staff_id,
            year=year_and_month['year'],
            month=year_and_month['month'],
        )
        for year_and_month in years_and_months
    ]
    StaffAvailableDate.objects.bulk_create(available_dates)
