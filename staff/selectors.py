from dataclasses import dataclass

from staff.exceptions import StaffNotFoundError
from staff.models import Staff

__all__ = ('get_staff_by_telegram_id', 'get_all_staff')


@dataclass(frozen=True, slots=True)
class StaffDTO:
    id: int
    telegram_id: int
    full_name: str
    car_sharing_phone_number: str
    console_phone_number: str
    is_banned: bool
    created_at: bool


def get_staff_by_telegram_id(telegram_id: int) -> Staff:
    try:
        return Staff.objects.get(telegram_id=telegram_id)
    except Staff.DoesNotExist:
        raise StaffNotFoundError


def get_all_staff() -> list[StaffDTO]:
    staff_list = (
        Staff.objects
        .order_by('full_name')
        .values(
            'id',
            'telegram_id',
            'full_name',
            'car_sharing_phone_number',
            'console_phone_number',
            'is_banned',
            'created_at'
        )
    )
    return [
        StaffDTO(
            id=staff['id'],
            telegram_id=staff['telegram_id'],
            full_name=staff['full_name'],
            car_sharing_phone_number=staff['car_sharing_phone_number'],
            console_phone_number=staff['console_phone_number'],
            is_banned=staff['is_banned'],
            created_at=staff['created_at']
        ) for staff in staff_list
    ]
