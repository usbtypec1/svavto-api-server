from dataclasses import dataclass

from shifts.exceptions import (
    DryCleaningRequestInvalidStatusError,
    DryCleaningRequestNotFoundError,
)
from shifts.models import (
    DryCleaningRequest, DryCleaningRequestPhoto,
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

        photo_file_ids = DryCleaningRequestPhoto.objects.filter(
            request=dry_cleaning_request,
        ).values_list('file_id', flat=True)
        services = DryCleaningRequestService.objects.filter(
            request=dry_cleaning_request,
        ).select_related('service')

        bot = get_telegram_bot()

        lines: list[str] = [
            '❌ Ваш запрос на химчистку отклонен',
            'Услуги:',
        ]

        for service in services:
            if service.service.is_countable:
                lines.append(
                    f'{service.service.name} - {service.count} шт.'
                )
            else:
                lines.append(service.service.name)

        caption = '\n'.join(lines)

        try_send_photos_media_group(
            bot=bot,
            file_ids=photo_file_ids,
            caption=caption,
            chat_id=dry_cleaning_request.shift.staff_id,
        )
