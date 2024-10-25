from dataclasses import dataclass
from datetime import datetime

from economics.models import Penalty, Surcharge
from mailing.services import try_send_message

__all__ = (
    'create_penalty_and_send_notification',
    'create_surcharge_and_send_notification',
)


@dataclass(frozen=True, slots=True)
class SurchargeCreateResult:
    id: int
    staff_id: int
    reason: str
    amount: int
    created_at: datetime
    is_notification_delivered: bool


@dataclass(frozen=True, slots=True)
class PenaltyCreateResult:
    id: int
    staff_id: int
    reason: str
    created_at: datetime
    is_notification_delivered: bool


def format_penalty_notification_text(
        reason: str
) -> str:
    return f'<b>🛑 Вы получили штраф по причине:</b> {reason}'


def create_penalty_and_send_notification(
        *,
        staff_id: int,
        reason: str,
) -> PenaltyCreateResult:
    penalty = Penalty.objects.create(
        staff_id=staff_id,
        reason=reason,
    )
    notification_text = format_penalty_notification_text(reason)
    is_notification_delivered = try_send_message(
        chat_id=staff_id,
        text=notification_text,
    )
    return PenaltyCreateResult(
        id=penalty.id,
        staff_id=penalty.staff_id,
        reason=penalty.reason,
        created_at=penalty.created_at,
        is_notification_delivered=is_notification_delivered,
    )


def format_surcharge_notification_text(
        reason: str,
        amount: int,
) -> str:
    return (
        f'<b>💰 Вы получили доплату в размере {amount}'
        f' по причине:</b> {reason}'
    )


def create_surcharge_and_send_notification(
        *,
        staff_id: int,
        reason: str,
        amount: int,
) -> SurchargeCreateResult:
    surcharge = Surcharge.objects.create(
        staff_id=staff_id,
        reason=reason,
        amount=amount,
    )
    notification_text = format_surcharge_notification_text(
        reason=reason,
        amount=amount,
    )
    is_notification_delivered = try_send_message(
        chat_id=staff_id,
        text=notification_text,
    )
    return SurchargeCreateResult(
        id=surcharge.id,
        staff_id=surcharge.staff_id,
        reason=surcharge.reason,
        amount=surcharge.amount,
        created_at=surcharge.created_at,
        is_notification_delivered=is_notification_delivered,
    )
