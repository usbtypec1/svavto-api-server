from dataclasses import dataclass

from dry_cleaning.exceptions import (
    DryCleaningRequestInvalidStatusError,
    DryCleaningRequestNotFoundError,
)
from dry_cleaning.models import (
    DryCleaningRequest,
    DryCleaningRequestPhoto,
    DryCleaningRequestService,
)
from telegram.services import get_telegram_bot, try_send_photos_media_group


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestRejectInteractor:
    dry_cleaning_request_id: int
    response_comment: str | None

    def execute(self) -> None:
        try:
            dry_cleaning_request = (
                DryCleaningRequest.objects
                .get(id=self.dry_cleaning_request_id)
            )
        except DryCleaningRequest.DoesNotExist:
            raise DryCleaningRequestNotFoundError

        if dry_cleaning_request.status != DryCleaningRequest.Status.PENDING:
            raise DryCleaningRequestInvalidStatusError

        dry_cleaning_request.status = DryCleaningRequest.Status.REJECTED
        dry_cleaning_request.response_comment = self.response_comment
        dry_cleaning_request.save(
            update_fields=(
                'status',
                'response_comment',
                'updated_at',
            ),
        )

        photo_urls = DryCleaningRequestPhoto.objects.filter(
            request=dry_cleaning_request,
        ).values_list('url', flat=True)
        services = DryCleaningRequestService.objects.filter(
            request=dry_cleaning_request,
        ).select_related('service')

        bot = get_telegram_bot()

        lines: list[str] = [
            '❌ Ваш запрос на химчистку отклонен',
            f'Гос.номер: {dry_cleaning_request.car_number}',
            'Услуги:',
        ]

        for service in services:
            if service.service.is_countable:
                lines.append(
                    f'{service.service.name} - {service.count} шт.'
                )
            else:
                lines.append(service.service.name)

        if self.response_comment:
            lines.append(f'Комментарий: {self.response_comment}')

        caption = '\n'.join(lines)

        try_send_photos_media_group(
            bot=bot,
            file_ids=photo_urls,
            caption=caption,
            chat_id=dry_cleaning_request.shift.staff_id,
        )
