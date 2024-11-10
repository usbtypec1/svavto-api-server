from django.db.models import QuerySet

from staff.exceptions import StaffNotFoundError
from staff.models import Staff

__all__ = (
    'get_staff_by_id',
    'get_all_staff',
    'ensure_staff_exists',
)


def get_staff_by_id(staff_id: int) -> Staff:
    try:
        return Staff.objects.get(id=staff_id)
    except Staff.DoesNotExist:
        raise StaffNotFoundError


def ensure_staff_exists(staff_id: int) -> None:
    if not Staff.objects.filter(id=staff_id).exists():
        raise StaffNotFoundError


def get_all_staff(
        *,
        order_by: str
) -> QuerySet[Staff]:
    return Staff.objects.order_by(order_by)
