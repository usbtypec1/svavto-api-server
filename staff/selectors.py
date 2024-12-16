import datetime
from dataclasses import dataclass
from typing import Iterable

from django.db.models import QuerySet

from staff.exceptions import StaffNotFoundError
from staff.models import Staff

__all__ = (
    'get_staff_by_id',
    'get_all_staff',
    'ensure_staff_exists',
    'get_staff',
    'StaffItem',
)


@dataclass(frozen=True, slots=True)
class StaffItem:
    id: int
    full_name: str
    car_sharing_phone_number: str
    console_phone_number: str
    created_at: datetime.datetime
    banned_at: datetime.datetime | None


def get_staff_by_id(staff_id: int) -> Staff:
    try:
        return Staff.objects.get(id=staff_id)
    except Staff.DoesNotExist:
        raise StaffNotFoundError


def ensure_staff_exists(staff_id: int) -> None:
    if not Staff.objects.filter(id=staff_id).exists():
        raise StaffNotFoundError


def get_all_staff(*, order_by: str) -> QuerySet[Staff]:
    return Staff.objects.order_by(order_by)


def get_staff(
        *,
        staff_ids: Iterable[int] | None = None,
) -> list[StaffItem]:
    staff_list = Staff.objects.all()

    if staff_ids is not None:
        staff_list = staff_list.filter(id__in=staff_ids)

    staff_list = staff_list.values(
        'id',
        'full_name',
        'car_sharing_phone_number',
        'console_phone_number',
        'created_at',
        'banned_at',
    ).order_by('full_name')

    return [
        StaffItem(
            id=staff['id'],
            full_name=staff['full_name'],
            car_sharing_phone_number=staff['car_sharing_phone_number'],
            console_phone_number=staff['console_phone_number'],
            created_at=staff['created_at'],
            banned_at=staff['banned_at'],
        )
        for staff in staff_list
    ]
