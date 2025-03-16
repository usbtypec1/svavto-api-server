import datetime
from collections.abc import Iterable
from dataclasses import dataclass
from enum import auto, StrEnum
from typing import Final, TypeAlias, TypedDict

from django.db import transaction

from economics.exceptions import (
    CarTransporterPenaltyNotFoundError,
    CarTransporterSurchargeNotFoundError,
    InvalidPenaltyConsequenceError,
)
from economics.models import Penalty, PenaltyPhoto, Surcharge
from economics.selectors import compute_staff_penalties_count
from shifts.selectors import get_shift_by_id
from telegram.services import (
    get_telegram_bot,
    try_send_message,
    try_send_photos_media_group,
)


class PenaltyReason(StrEnum):
    NOT_SHOWING_UP = auto()
    EARLY_LEAVE = auto()
    LATE_REPORT = auto()


@dataclass(frozen=True, slots=True)
class PenaltyAmountAndConsequence:
    amount: int
    consequence: str | None


class PenaltyConfig(TypedDict):
    threshold: int | float
    amount: int
    consequence: Penalty.Consequence | None


PenaltyConfigs: TypeAlias = tuple[PenaltyConfig, ...]
PenaltyReasonToConfigs: TypeAlias = dict[PenaltyReason, PenaltyConfigs]

PENALTY_CONFIGS: Final[PenaltyReasonToConfigs] = {
    PenaltyReason.LATE_REPORT: (
        {
            "threshold": 0,
            "amount": 0,
            "consequence": Penalty.Consequence.WARN,
        },
        {
            "threshold": 1,
            "amount": 100,
            "consequence": None,
        },
        {
            "threshold": float("inf"),
            "amount": 300,
            "consequence": None,
        },
    ),
    PenaltyReason.NOT_SHOWING_UP: (
        {
            "threshold": 0,
            "amount": 500,
            "consequence": None,
        },
        {
            "threshold": 1,
            "amount": 1000,
            "consequence": None,
        },
        {
            "threshold": 2,
            "amount": 1000,
            "consequence": Penalty.Consequence.DISMISSAL,
        },
        {
            "threshold": float("inf"),
            "amount": 0,
            "consequence": Penalty.Consequence.DISMISSAL,
        },
    ),
}


def compute_penalty_amount_and_consequence(
    *,
    staff_id: int,
    reason: PenaltyReason | str,
) -> PenaltyAmountAndConsequence:
    """
    Compute penalty amount and consequence based on staff violation reason
    and history.

    Args:
        staff_id: The ID of the staff member
        reason: The reason for the penalty

    Returns:
        PenaltyAmountAndConsequence with calculated amount and potential
        consequence

    Raises:
        InvalidPenaltyConsequenceError if an unsupported penalty reason is
        provided
    """
    if reason == PenaltyReason.EARLY_LEAVE:
        return PenaltyAmountAndConsequence(amount=1000, consequence=None)

    penalties_count = compute_staff_penalties_count(
        staff_id=staff_id,
        reason=reason,
    )

    penalty_config = PENALTY_CONFIGS.get(reason, tuple())

    for config in penalty_config:
        threshold = config["threshold"]
        amount = config["amount"]
        consequence = config["consequence"]

        if penalties_count <= threshold:
            return PenaltyAmountAndConsequence(amount=amount, consequence=consequence)

    raise InvalidPenaltyConsequenceError(
        staff_id=staff_id,
        penalty_reason=reason,
        penalties_count=penalties_count,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class PenaltyCreateResult:
    id: int
    staff_id: int
    staff_full_name: str
    shift_id: int
    shift_date: datetime.date
    reason: str
    consequence: str | None
    amount: int
    photo_urls: list[str]
    created_at: datetime.datetime


@transaction.atomic
def create_penalty(
    *,
    shift_id: int,
    reason: str,
    amount: int | None,
    photo_urls: Iterable[str],
) -> PenaltyCreateResult:
    """
    Give penalty for staff member.
    If penalty amount is not provided,
    it will be automatically computed from penalty reason.

    Keyword Args:
        shift_id: shift penalty related to.
        reason: reason for penalty.
        amount: penalty amount.
        photo_urls: penalty photo urls.

    Returns:
        Created penalty.
    """
    shift = get_shift_by_id(shift_id)
    photo_urls = list(photo_urls)

    consequence: str | None = None
    if amount is None:
        penalty_amount_and_consequence = compute_penalty_amount_and_consequence(
            staff_id=shift.staff_id,
            reason=reason,
        )
        amount = penalty_amount_and_consequence.amount
        consequence = penalty_amount_and_consequence.consequence

    penalty = Penalty(
        shift_id=shift_id,
        reason=reason,
        amount=amount,
        consequence=consequence,
    )
    penalty.save()

    photos = [
        PenaltyPhoto(penalty=penalty, photo_url=photo_url) for photo_url in photo_urls
    ]
    PenaltyPhoto.objects.bulk_create(photos)

    bot = get_telegram_bot()
    penalty_notification_text = (
        "<b>❗️ Вы получили новый штраф:</b>"
        f"\nСумма: {amount} рублей"
        f"\nПричина: {reason}"
    )
    if photo_urls:
        try_send_photos_media_group(
            bot=bot,
            chat_id=shift.staff_id,
            file_ids=photo_urls,
            caption=penalty_notification_text,
        )
    else:
        try_send_message(
            bot=bot,
            chat_id=shift.staff_id,
            text=penalty_notification_text,
        )

    return PenaltyCreateResult(
        id=penalty.id,
        staff_id=shift.staff_id,
        staff_full_name=shift.staff.full_name,
        shift_id=shift_id,
        shift_date=shift.date,
        reason=reason,
        consequence=consequence,
        amount=amount,
        photo_urls=photo_urls,
        created_at=penalty.created_at,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class CarTransporterPenaltyDeleteInteractor:
    penalty_id: int

    def execute(self) -> None:
        deleted_count = Penalty.objects.filter(id=self.penalty_id).delete()
        if deleted_count == 0:
            raise CarTransporterPenaltyNotFoundError


@dataclass(frozen=True, slots=True, kw_only=True)
class CarTransporterSurchargeDeleteInteractor:
    surcharge_id: int

    def execute(self) -> None:
        deleted_count = Surcharge.objects.filter(id=self.surcharge_id).delete()
        if deleted_count == 0:
            raise CarTransporterSurchargeNotFoundError
