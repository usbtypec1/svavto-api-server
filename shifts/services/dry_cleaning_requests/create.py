import contextlib
import datetime
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID, uuid4

import cloudinary.uploader
from django.conf import settings
from django.db import transaction
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from shifts.models.dry_cleaning_requests import (
    DryCleaningRequest,
    DryCleaningRequestPhoto,
    DryCleaningRequestService,
)
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
    car_number: str
    photo_urls: list[str]
    services: Iterable[DryCleaningRequestServiceDto]
    status: int
    response_comment: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


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

        urls: list[str] = []
        for photo_file_id in self.photo_file_ids:
            url = bot.get_file_url(photo_file_id)
            url = cloudinary.uploader.upload(
                url,
                folder='svavto',
                public_id=uuid4().hex,
            )['secure_url']
            urls.append(url)

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

        lines: list[str] = ['<b>Запрашиваемые услуги:</b>']
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
