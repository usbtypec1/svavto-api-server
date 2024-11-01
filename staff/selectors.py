from dataclasses import dataclass

from staff.exceptions import StaffNotFoundError
from staff.models import Staff

__all__ = (
    'get_staff_by_id',
    'get_all_staff',
    'StaffDTO',
    'ensure_staff_exists',
)


@dataclass(frozen=True, slots=True)
class StaffDTO:
    id: int
    full_name: str
    car_sharing_phone_number: str
    console_phone_number: str
    is_banned: bool
    created_at: bool


def get_staff_by_id(staff_id: int) -> Staff:
    try:
        return (
            Staff.objects
            .prefetch_related('staffavailabledate_set')
            .get(id=staff_id)
        )
    except Staff.DoesNotExist:
        raise StaffNotFoundError


def ensure_staff_exists(staff_id: int) -> None:
    if not Staff.objects.filter(id=staff_id).exists():
        raise StaffNotFoundError


def get_all_staff() -> list[StaffDTO]:
    staff_list = (
        Staff.objects
        .order_by('full_name')
        .values(
            'id',
            'full_name',
            'car_sharing_phone_number',
            'console_phone_number',
            'banned_at',
            'created_at'
        )
    )
    return [
        StaffDTO(
            id=staff['id'],
            full_name=staff['full_name'],
            car_sharing_phone_number=staff['car_sharing_phone_number'],
            console_phone_number=staff['console_phone_number'],
            is_banned=bool(staff['banned_at']),
            created_at=staff['created_at']
        ) for staff in staff_list
    ]
