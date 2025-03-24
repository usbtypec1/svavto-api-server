import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from economics.models import CarTransporterPenalty, PenaltyPhoto
from economics.services.penalties import (
    compute_penalty_amount_and_consequence, PenaltyCreateResult,
)
from staff.selectors import get_staff_by_id
from telegram.services import (
    get_telegram_bot, try_send_message,
    try_send_photos_media_group,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CarTransporterPenaltyCreateUseCase:
    """
    Give penalty for staff member.
    If penalty amount is not provided,
    it will be automatically computed from penalty reason.

    Args:
        staff_id: staff member id.
        reason: reason for penalty.
        amount: penalty amount.
        photo_urls: penalty photo urls.

    Returns:
        Created penalty.
    """

    staff_id: int
    date: datetime.date
    reason: str
    amount: int | None
    photo_urls: Iterable[str]

    def execute(self) -> PenaltyCreateResult:
        staff = get_staff_by_id(self.staff_id)
        photo_urls = list(self.photo_urls)

        amount = self.amount
        consequence: str | None = None
        if amount is None:
            penalty_amount_and_consequence = (
                compute_penalty_amount_and_consequence(
                    staff_id=self.staff_id,
                    reason=self.reason,
                )
            )
            amount = penalty_amount_and_consequence.amount
            consequence = penalty_amount_and_consequence.consequence

        penalty = CarTransporterPenalty(
            staff_id=self.staff_id,
            date=self.date,
            reason=self.reason,
            amount=amount,
            consequence=consequence,
        )
        penalty.save()

        photos = [
            PenaltyPhoto(penalty=penalty, photo_url=photo_url)
            for photo_url in photo_urls
        ]
        PenaltyPhoto.objects.bulk_create(photos)

        bot = get_telegram_bot()
        penalty_notification_text = (
            "<b>❗️ Вы получили новый штраф:</b>"
            f"\nСумма: {amount} рублей"
            f"\nПричина: {self.reason}"
        )
        if photo_urls:
            try_send_photos_media_group(
                bot=bot,
                chat_id=self.staff_id,
                file_ids=photo_urls,
                caption=penalty_notification_text,
            )
        else:
            try_send_message(
                bot=bot,
                chat_id=self.staff_id,
                text=penalty_notification_text,
            )

        return PenaltyCreateResult(
            id=penalty.id,
            staff_id=self.staff_id,
            staff_full_name=staff.full_name,
            date=self.date,
            reason=self.reason,
            consequence=consequence,
            amount=amount,
            photo_urls=photo_urls,
            created_at=penalty.created_at,
        )
