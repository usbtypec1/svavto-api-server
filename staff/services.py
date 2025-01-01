from django.db import IntegrityError
from django.utils import timezone

from staff.exceptions import (
    StaffAlreadyExistsError,
    StaffNotFoundError,
)
from staff.models import Staff

__all__ = ('create_staff', 'update_staff', 'update_last_activity_time')


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
            console_phone_number=console_phone_number,
        )
    except IntegrityError:
        raise StaffAlreadyExistsError


def update_staff(
        *,
        staff_id: int,
        is_banned: bool,
) -> None:
    banned_at = timezone.now() if is_banned else None
    is_updated = Staff.objects.filter(id=staff_id).update(banned_at=banned_at)
    if not is_updated:
        raise StaffNotFoundError


def update_last_activity_time(*, staff_id: int) -> None:
    now = timezone.now()
    Staff.objects.filter(id=staff_id).update(last_activity_at=now)
