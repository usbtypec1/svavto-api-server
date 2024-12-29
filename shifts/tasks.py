import collections
import datetime
import time
from collections.abc import Iterable
from dataclasses import dataclass

from celery import shared_task
from django.db.models import QuerySet

from core.services import get_current_shift_date, to_moscow_timezone
from shifts.models import CarToWash, CarToWashAdditionalService, Shift
from staff.selectors import get_admin_ids
from telegram.services import (
    get_telegram_bot,
    try_send_message,
    try_send_photos_media_group,
)


@dataclass(frozen=True, slots=True)
class ShiftSummary:
    staff_full_name: str
    car_wash_name: str
    started_at: datetime.datetime | None
    finished_at: datetime.datetime | None
    comfort_cars_count: int
    business_cars_count: int
    vans_count: int
    planned_cars_count: int
    urgent_cars_count: int
    dry_cleaning_count: int
    total_cars_count: int
    refilled_cars_count: int
    not_refilled_cars_count: int
    finish_photo_file_ids: list[str]

    @property
    def is_started(self) -> bool:
        return self.started_at is not None

    @property
    def is_finished(self) -> bool:
        return self.finished_at is not None


def format_started_shifts(shifts: Iterable[ShiftSummary]) -> str:
    lines: list[str] = [f'Список подтвердивших смену на сегодня:']
    for shift in shifts:
        lines.append(
            f'📍 {shift.staff_full_name}'
            f' - в {to_moscow_timezone(shift.started_at):%H:%M}'
        )
    return '\n'.join(lines)


def format_not_started_shifts(shifts: Iterable[ShiftSummary]):
    lines: list[str] = [
        f'Список не подтвердивших смену на сегодня:'
    ]
    for shift in shifts:
        lines.append(f'📍 {shift.staff_full_name}')
    return '\n'.join(lines)


def format_finished_shift(shift: ShiftSummary) -> str:
    caption = [
        f'Перегонщик: {shift.staff_full_name}',
        f'Мойка: {shift.car_wash_name}',
        f'Всего: {shift.total_cars_count}',
        f'Плановая мойка: {shift.planned_cars_count}',
        f'🔶 Эконом: {shift.comfort_cars_count}',
        f'🔶 Бизнес: {shift.business_cars_count}',
        f'🔶 Фургон: {shift.vans_count}',
        f'Срочная мойка: {shift.urgent_cars_count}',
        f'Химчистки: {shift.dry_cleaning_count}',
        f'Долив: {shift.refilled_cars_count}',
        f'Недолив: {shift.not_refilled_cars_count}',
    ]
    return '\n'.join(caption)


def get_shift_summaries(date: datetime.date) -> list[ShiftSummary]:
    shifts: QuerySet[Shift] = (
        Shift.objects.select_related('staff', 'car_wash')
        .prefetch_related(
            'cartowash_set',
            'cartowash_set__additional_services__service',
            'finish_photos',
        )
        .filter(date=date)
    )

    summaries: list[ShiftSummary] = []

    for shift in shifts:
        if shift.car_wash is not None:
            car_wash_name = shift.car_wash.name
        else:
            car_wash_name = 'Не указано'

        car_class_to_count = collections.defaultdict(int)
        wash_type_to_count = collections.defaultdict(int)
        refilled_cars_count = 0
        dry_cleaning_count = 0

        cars_to_wash: QuerySet[CarToWash] = shift.cartowash_set.all()
        for car_to_wash in cars_to_wash:
            car_to_wash: CarToWash
            car_class_to_count[car_to_wash.car_class] += 1
            wash_type_to_count[car_to_wash.wash_type] += 1
            dry_cleaning_count += bool(
                car_to_wash.windshield_washer_refilled_bottle_percentage
            )

            additional_services: QuerySet[CarToWashAdditionalService] = (
                car_to_wash.additional_services.all()
            )
            for additional_service in additional_services:
                dry_cleaning_count += additional_service.service.is_dry_cleaning

        total_cars_count = sum(car_class_to_count.values())
        not_refilled_cars_count = total_cars_count - refilled_cars_count

        comfort_cars_count = car_class_to_count[CarToWash.CarType.COMFORT]
        business_cars_count = car_class_to_count[CarToWash.CarType.BUSINESS]
        vans_count = car_class_to_count[CarToWash.CarType.VAN]
        planned_cars_count = wash_type_to_count[CarToWash.WashType.PLANNED]
        urgent_cars_count = wash_type_to_count[CarToWash.WashType.URGENT]

        if shift.is_finished:
            file_ids = shift.finish_photos.values_list(
                'file_id',
                flat=True,
            )
        else:
            file_ids = []

        summaries.append(
            ShiftSummary(
                staff_full_name=shift.staff.full_name,
                car_wash_name=car_wash_name,
                started_at=shift.started_at,
                finished_at=shift.finished_at,
                comfort_cars_count=comfort_cars_count,
                business_cars_count=business_cars_count,
                vans_count=vans_count,
                planned_cars_count=planned_cars_count,
                urgent_cars_count=urgent_cars_count,
                dry_cleaning_count=dry_cleaning_count,
                total_cars_count=total_cars_count,
                refilled_cars_count=refilled_cars_count,
                not_refilled_cars_count=not_refilled_cars_count,
                finish_photo_file_ids=file_ids,
            )
        )

    return summaries


@shared_task
def send_today_shifts_report():
    shift_date = get_current_shift_date()
    bot = get_telegram_bot()

    admin_staff_ids = get_admin_ids()

    shifts = get_shift_summaries(shift_date)

    started_shifts = [shift for shift in shifts if shift.is_started]
    not_started_shifts = [shift for shift in shifts if not shift.is_started]
    finished_shifts = [shift for shift in shifts if shift.is_finished]

    text_messages: list[str] = []
    media_messages: list[dict] = []

    if started_shifts:
        text_messages.append(format_started_shifts(started_shifts))

    if not_started_shifts:
        text_messages.append(format_not_started_shifts(not_started_shifts))

    for shift in finished_shifts:
        text = format_finished_shift(shift)
        if shift.finish_photo_file_ids:
            media_messages.append({
                'file_ids': shift.finish_photo_file_ids,
                'text': text,
            })
        else:
            text_messages.append(text)

    for admin_staff_id in admin_staff_ids:
        for text in text_messages:
            try_send_message(bot=bot, chat_id=admin_staff_id, text=text)
            time.sleep(1)
        for media_message in media_messages:
            file_ids = media_message['file_ids']
            text = media_message['text']
            try_send_photos_media_group(
                bot=bot,
                chat_id=admin_staff_id,
                caption=text,
                file_ids=file_ids,
            )
            time.sleep(1)
