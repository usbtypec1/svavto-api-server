from django.core.management import BaseCommand

from django.core.management import BaseCommand

from core.services import get_current_shift_date
from shifts.models import Shift
from shifts.services import ShiftSummaryInteractor
from shifts.services.shifts.finish import (
    CarWashTransferredCarsSummary,
    ShiftSummary,
)
from telegram.services import (
    get_telegram_bot, try_get_chat_username, try_send_photos_media_group,
)


def format_shift_car_wash_finish_summary(
        car_wash_summary: CarWashTransferredCarsSummary,
) -> str:
    return (
        f'\nМойка: {car_wash_summary.car_wash_name}'
        f'\nВсего: {car_wash_summary.total_cars_count}'
        f'\n🔶 Комфорт: {car_wash_summary.comfort_cars_count}'
        f'\n🔶 Бизнес: {car_wash_summary.business_cars_count}'
        f'\n🔶 Фургон: {car_wash_summary.vans_count}'
        f'\nПлановая мойка: {car_wash_summary.planned_cars_count}'
        f'\nСрочная мойка: {car_wash_summary.urgent_cars_count}'
        f'\nХимчистки: {car_wash_summary.dry_cleaning_count}'
        f'\nПБ: {car_wash_summary.trunk_vacuum_count}'
        f'\nДолив: {car_wash_summary.refilled_cars_count}'
        f'\nНедолив: {car_wash_summary.not_refilled_cars_count}'
    )


def format_shift_finish_text(
        shift_summary: ShiftSummary, username: str | None
) -> str:
    lines: list[str] = []
    if username is None:
        lines.append(f'Перегонщик: {shift_summary.staff_full_name}')
    else:
        lines.append(
            f'Перегонщик: {shift_summary.staff_full_name} (@{username})'
        )
    for car_wash_summary in shift_summary.car_washes:
        lines.append(format_shift_car_wash_finish_summary(car_wash_summary))
    if not shift_summary.car_washes:
        lines.append('\nНет добавленных авто')
    return '\n'.join(lines)


class Command(BaseCommand):
    help = 'Send shift finish reports'

    def add_arguments(self, parser):
        parser.add_argument(
            'chat_id',
            type=int,
            help='Telegram chat id to send the report',
        )

    def handle(self, *args, **options):
        bot = get_telegram_bot()

        chat_id: int = options['chat_id']
        self.stdout.write(f'Sending shift finish report to chat {chat_id}')

        date = get_current_shift_date()
        shifts = Shift.objects.prefetch_related('finish_photos').filter(
            date=date,
            finished_at__isnull=False,
        )
        for shift in shifts:
            interactor = ShiftSummaryInteractor(shift_id=shift.id)
            shift_summary = interactor.execute()

            photo_file_ids = [
                photo.file_id for photo in shift.finish_photos.all()
            ]

            username = try_get_chat_username(
                bot=bot,
                chat_id=shift_summary.staff_id,
            )

            text = format_shift_finish_text(shift_summary, username=username)
            is_sent = try_send_photos_media_group(
                bot=bot,
                chat_id=chat_id,
                file_ids=photo_file_ids,
                caption=text,
            )
            if is_sent:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Shift finish report has been sent for staff '
                        f'{shift.staff_id}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Shift finish report has been sent for staff '
                        f'{shift.staff_id}'
                    )
                )
