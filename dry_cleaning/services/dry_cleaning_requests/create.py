import datetime
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from django.conf import settings
from django.db import transaction
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import TeleBot

from dry_cleaning.models import (
    DryCleaningRequest,
    DryCleaningRequestPhoto,
    DryCleaningRequestService,
)
from photo_upload.services import upload_via_url, upload_via_urls
from shifts.services.shifts.validators import ensure_shift_exists
from telegram.services import (
    get_dry_cleaning_telegram_bot, get_telegram_bot, try_send_message,
    try_send_photos_media_group,
)


class HasIdAndCount(TypedDict):
    id: UUID
    count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestServiceDto:
    id: UUID
    name: str
    count: int
    is_countable: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestCreateResponseDto:
    id: int
    shift_id: int
    staff_id: int
    staff_full_name: str
    car_number: str
    photo_urls: list[str]
    services: Iterable[DryCleaningRequestServiceDto]
    status: int
    response_comment: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


def get_file_urls(bot: TeleBot, file_ids: Iterable[str]) -> list[str]:
    with ThreadPoolExecutor() as executor:
        return list(executor.map(bot.get_file_url, file_ids))


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestCreateInteractor:
    shift_id: int
    car_number: str
    photo_file_ids: Iterable[str]
    services: Iterable[HasIdAndCount]

    @transaction.atomic
    def execute(self) -> DryCleaningRequestCreateResponseDto:
        ensure_shift_exists(self.shift_id)
        dry_cleaning_request = DryCleaningRequest.objects.create(
            shift_id=self.shift_id,
            car_number=self.car_number,
        )
        bot = get_telegram_bot()

        urls = get_file_urls(bot, self.photo_file_ids)
        urls = [
            uploaded_photo.url
            for uploaded_photo in upload_via_urls(urls, folder='dry_cleaning')
        ]

        photos = DryCleaningRequestPhoto.objects.bulk_create(
            DryCleaningRequestPhoto(
                request=dry_cleaning_request,
                url=url,
            )
            for url in urls
        )
        services = DryCleaningRequestService.objects.bulk_create(
            DryCleaningRequestService(
                request=dry_cleaning_request,
                service_id=service['id'],
                count=service['count'],
            )
            for service in self.services
        )

        callback_data = (f'dry_cleaning_request:{dry_cleaning_request.id}:'
                         f'{settings.DEPARTMENT_NAME}')
        button = InlineKeyboardButton(
            text='Проверить',
            callback_data=callback_data,
        )
        reply_markup = InlineKeyboardMarkup(keyboard=[[button]])

        lines: list[str] = [
            f'<b>Сотрудник {dry_cleaning_request.shift.staff.full_name} '
            'запрашивает химчистку</b>',
            f'Гос.номер: {dry_cleaning_request.car_number}',
        ]
        for service in services:
            if service.service.is_countable:
                lines.append(f'{service.service.name} - {service.count} шт.')
            else:
                lines.append(service.service.name)

        photo_urls = [photo.url for photo in photos]

        bot = get_dry_cleaning_telegram_bot()
        for chat_id in settings.DRY_CLEANING_USER_IDS:
            try_send_photos_media_group(
                bot=bot,
                file_ids=photo_urls,
                chat_id=chat_id,
                caption='\n'.join(lines)
            )

            try_send_message(
                bot=bot,
                reply_markup=reply_markup,
                text='Новый запрос на химчистку',
                chat_id=chat_id,
            )

        return DryCleaningRequestCreateResponseDto(
            id=dry_cleaning_request.id,
            shift_id=dry_cleaning_request.shift_id,
            staff_id=dry_cleaning_request.shift.staff_id,
            staff_full_name=dry_cleaning_request.shift.staff.full_name,
            car_number=dry_cleaning_request.car_number,
            photo_urls=photo_urls,
            services=[
                DryCleaningRequestServiceDto(
                    id=service.service_id,
                    name=service.service.name,
                    count=service.count,
                    is_countable=service.service.is_countable,
                )
                for service in services
            ],
            status=dry_cleaning_request.status,
            response_comment=dry_cleaning_request.response_comment,
            created_at=dry_cleaning_request.created_at,
            updated_at=dry_cleaning_request.updated_at,
        )
