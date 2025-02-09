import datetime
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from staff.exceptions import (
    StaffRegisterRequestAlreadyExistsError, StaffNotFoundError,
)
from staff.models import Staff, StaffRegisterRequest
from staff.selectors import ensure_staff_not_exists

__all__ = (
    'StaffRegisterRequestAcceptInteractor',
    'update_staff',
    'update_last_activity_time',
    'StaffRegisterRequestCreateInteractor',
    'StaffRegisterRequestRejectInteractor',
)

from telegram.services import get_telegram_bot, try_send_message


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffCreateResult:
    id: int
    full_name: str
    car_sharing_phone_number: str
    console_phone_number: str
    created_at: datetime.datetime
    banned_at: datetime.datetime | None
    last_activity_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffRegisterRequestCreateResult:
    id: int
    staff_id: int
    full_name: str
    car_sharing_phone_number: str
    console_phone_number: str
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffRegisterRequestCreateInteractor:
    staff_id: int
    full_name: str
    car_sharing_phone_number: str
    console_phone_number: str

    def execute(self):
        ensure_staff_not_exists(self.staff_id)

        staff_register_request = StaffRegisterRequest(
            staff_id=self.staff_id,
            full_name=self.full_name,
            car_sharing_phone_number=self.car_sharing_phone_number,
            console_phone_number=self.console_phone_number,
        )

        try:
            staff_register_request.full_clean()
            staff_register_request.save()
        except (IntegrityError, ValidationError):
            raise StaffRegisterRequestAlreadyExistsError

        return StaffRegisterRequestCreateResult(
            id=staff_register_request.id,
            staff_id=staff_register_request.staff_id,
            full_name=staff_register_request.full_name,
            car_sharing_phone_number=(
                staff_register_request.car_sharing_phone_number
            ),
            console_phone_number=staff_register_request.console_phone_number,
            created_at=staff_register_request.created_at,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffRegisterRequestAcceptInteractor:
    request_id: int

    @transaction.atomic
    def execute(self) -> StaffCreateResult:
        try:
            staff_registration_request = StaffRegisterRequest.objects.get(
                id=self.request_id
            )
        except StaffRegisterRequest.DoesNotExist:
            raise StaffNotFoundError

        ensure_staff_not_exists(staff_registration_request.staff_id)

        staff = Staff(
            id=staff_registration_request.staff_id,
            full_name=staff_registration_request.full_name,
            car_sharing_phone_number=(
                staff_registration_request.car_sharing_phone_number
            ),
            console_phone_number=(
                staff_registration_request.console_phone_number
            ),
        )
        staff.full_clean()
        staff.save()
        staff_registration_request.delete()

        bot = get_telegram_bot()
        try_send_message(
            bot=bot,
            chat_id=staff.id,
            text=(
                '✅ Ваша запрос на регистрацию принят!'
                ' Введите /start для начала работы.'
            ),
        )

        return StaffCreateResult(
            id=staff.id,
            full_name=staff.full_name,
            car_sharing_phone_number=staff.car_sharing_phone_number,
            console_phone_number=staff.console_phone_number,
            created_at=staff.created_at,
            banned_at=staff.banned_at,
            last_activity_at=staff.last_activity_at,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffRegisterRequestRejectInteractor:
    request_id: int

    def execute(self) -> None:
        deleted_count, _ = (
            StaffRegisterRequest.objects
            .filter(id=self.request_id)
            .delete()
        )
        if not deleted_count:
            raise StaffNotFoundError

        bot = get_telegram_bot()
        try_send_message(
            bot=bot,
            chat_id=self.request_id,
            text='❌ Ваша заявка на регистрацию отклонена.',
        )


def update_staff(
        *,
        staff_id: int,
        is_banned: bool,
) -> None:
    banned_at = timezone.now() if is_banned else None
    is_updated = Staff.objects.filter(id=staff_id).update(banned_at=banned_at)
    update_last_activity_time(staff_id=staff_id)
    if not is_updated:
        raise StaffNotFoundError


def update_last_activity_time(*, staff_id: int) -> None:
    now = timezone.now()
    Staff.objects.filter(id=staff_id).update(last_activity_at=now)
