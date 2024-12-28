import collections
import time
from datetime import datetime, timedelta
from uuid import UUID

from celery import shared_task
from django.utils import timezone

from shifts.models import CarToWash, Shift
from staff.models import AdminStaff
from telegram.services import (
    get_telegram_bot,
    try_send_message,
    try_send_photos_media_group,
)


def to_moscow_time(date: datetime):
    return date + timedelta(hours=3)


DRY_CLEANING_SERVICE_IDS = (
    UUID('439b8819-c153-4409-abaf-6c762a525e19'),
    UUID('10ca1e3d-e8b2-4892-b10e-067807824849'),
    UUID('89d971bb-5845-449b-9f17-d30f084c04e0'),
    UUID('3b98ad3d-b117-47ba-a58c-c83763fe461a'),
    UUID('5433d5aa-6a11-4f69-954f-e1ab6e0cffbe'),
    UUID('1a4341b2-8262-4958-a9ac-e740bd5afbc0'),
    UUID('7ef898cb-4ace-48f9-8082-f1197304d1cb'),
    UUID('aed36e39-ceda-4c8b-9dc1-92720f46b6fe'),
    UUID('bff1ca39-51bd-48b5-b3b5-a07732862f08'),
    UUID('0d4ef51d-2f35-4aee-8b45-a629be9fba23'),
    UUID('d0cfa900-7f27-43e1-b919-b3b2e0df1f23'),
    UUID('9ce535e0-1161-4cf4-8edb-3d57c356dca7'),
    UUID('3504f046-aacd-4bf4-8381-7f5fde536b44'),
    UUID('fadb3316-78d9-455c-ab5a-88a5585f9fd9'),
    UUID('6585af13-96b1-4c26-bcbc-5b5cbbf3438f'),
    UUID('10c7d6a1-9f02-475d-ae79-2bff4707f28a'),
    UUID('3c995a7a-0ebc-44ad-8c3a-7130fb937109'),
    UUID('de2a34f9-9e5f-4659-b68e-275b2116f299'),
    UUID('766e7d8c-763f-4977-886a-73bca59e40ec'),
    UUID('4324cba0-d239-411c-b2e8-938aed3a2e50'),
    UUID('27c77213-a8bb-4490-a06b-20e65c93eb30'),
    UUID('0d5d18aa-2c9a-4461-8296-d6ddd057683b'),
    UUID('e1e4b418-472c-45bb-9c1c-9e7716530147'),
    UUID('d403ced7-0911-42f7-a85f-2f1926168dd9'),
    UUID('b5e21bb0-e811-4c26-950e-b4228e71f796'),
    UUID('0fa5f8c5-2c5e-428f-96ec-30c5ba694b3a'),
    UUID('34fca142-ac6c-4270-b6c1-68dd594cfddd'),
    UUID('7d36335c-3a89-46dc-a11d-7906246fc736'),
)


@shared_task
def send_today_shifts_report():
    now = to_moscow_time(timezone.now())
    bot = get_telegram_bot()

    shifts = (
        Shift.objects.select_related('staff', 'car_wash')
        .prefetch_related(
            'cartowash_set',
            'cartowash_set__additional_services',
        )
        .filter(date=now.date())
    )

    admin_staff_ids = AdminStaff.objects.values_list('id', flat=True)

    started_shifts = [shift for shift in shifts if shift.is_started]
    not_started_shifts = [shift for shift in shifts if not shift.is_started]
    finished_shifts = [shift for shift in shifts if shift.is_finished]

    if started_shifts:
        started_shifts_staff = [
            (
                f'📍 {shift.staff.full_name}'
                f' - в {to_moscow_time(shift.started_at):H:M}'
            )
            for shift in started_shifts
        ]
        started_shifts_message_lines: list[str] = [
            f'Список подтвердивших смену на сегодня:'
        ]
        started_shifts_message_lines += started_shifts_staff
        started_shifts_message = '\n'.join(started_shifts_message_lines)

        for admin_staff_id in admin_staff_ids:
            try_send_message(
                bot=bot,
                chat_id=admin_staff_id,
                text=started_shifts_message,
            )
            time.sleep(1)

    if not_started_shifts:
        not_started_shifts_staff = [
            f'📍 {shift.staff.full_name}' for shift in not_started_shifts
        ]
        not_started_shifts_message_lines: list[str] = [
            f'Список не подтвердивших смену на сегодня:'
        ]
        not_started_shifts_message_lines += not_started_shifts_staff
        not_started_shifts_message = '\n'.join(not_started_shifts_message_lines)

        for admin_staff_id in admin_staff_ids:
            try_send_message(
                bot=bot,
                chat_id=admin_staff_id,
                text=not_started_shifts_message,
            )
            time.sleep(1)

    for shift in finished_shifts:
        if shift.car_wash is not None:
            car_wash_name = shift.car_wash.name
        else:
            car_wash_name = 'Не указано'

        car_class_to_count = collections.defaultdict(int)
        wash_type_to_count = collections.defaultdict(int)
        refilled_cars_count = 0
        dry_cleaning_count = 0

        for car_to_wash in shift.cartowash_set.all():
            car_to_wash: CarToWash
            car_class_to_count[car_to_wash.car_class] += 1
            wash_type_to_count[car_to_wash.wash_type] += 1
            if car_to_wash.windshield_washer_refilled_bottle_percentage != 0:
                refilled_cars_count += 1

            for (
                additional_service
            ) in car_to_wash.additional_services.all():
                additional_service_id = additional_service.service_id
                if additional_service_id in DRY_CLEANING_SERVICE_IDS:
                    dry_cleaning_count += additional_service.count

        total_cars_count = sum(car_class_to_count.values())
        not_refilled_cars_count = total_cars_count - refilled_cars_count

        caption = [
            f'Перегонщик: {shift.staff.full_name}',
            f'Мойка: {car_wash_name}',
            f'Всего: {total_cars_count}',
            f'Плановая мойка: {wash_type_to_count[CarToWash.WashType.PLANNED]}',
            f'🔶 Эконом: {car_class_to_count[CarToWash.CarType.COMFORT]}',
            f'🔶 Бизнес: {car_class_to_count[CarToWash.CarType.BUSINESS]}',
            f'🔶 Фургон: {car_class_to_count[CarToWash.CarType.VAN]}',
            f'Срочная мойка: {wash_type_to_count[CarToWash.WashType.URGENT]}',
            f'Химчистки: {dry_cleaning_count}',
            f'Долив: {refilled_cars_count}',
            f'Недолив: {not_refilled_cars_count}',
        ]
        caption = '\n'.join(caption)
        try_send_photos_media_group(
            bot=bot,
            chat_id=admin_staff_ids,
            file_ids=[
                shift.statement_photo_file_id,
                shift.service_app_photo_file_id,
            ],
            caption=caption,
        )
        time.sleep(1)
