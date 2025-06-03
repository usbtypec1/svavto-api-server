from django.core.management.base import BaseCommand

from photo_upload.services import upload_via_url
from shifts.models import ShiftFinishPhoto
from telegram.services import get_file_urls, get_telegram_bot


class Command(BaseCommand):
    help = (
        "Fetches Telegram file URLs"
        " for ShiftFinishPhoto records without a URL"
    )

    def handle(self, *args, **options):
        bot = get_telegram_bot()
        photo_file_ids = (
            ShiftFinishPhoto.objects
            .filter(url__isnull=True)
            .values_list("file_id", flat=True)
            .distinct()
        )

        total = len(photo_file_ids)
        self.stdout.write(f"Found {total} photo(s) with missing URLs")

        for i, file_id in enumerate(photo_file_ids, start=1):
            self.stdout.write(f"[{i}/{total}] Processing file_id: {file_id}")

            try:
                telegram_file_urls = get_file_urls(bot=bot, file_ids=[file_id])
                if not telegram_file_urls:
                    self.stdout.write(self.style.WARNING(
                        f"No Telegram URL returned for file_id: {file_id}")
                    )
                    continue

                telegram_file_url = telegram_file_urls[0]

                url = upload_via_url(
                    url=telegram_file_url,
                    folder="shift_finish_photos",
                )
                updated = (
                    ShiftFinishPhoto.objects
                    .filter(file_id=file_id)
                    .update(url=url)
                )
                self.stdout.write(self.style.SUCCESS(
                    f"Updated {updated} row(s) for file_id: {file_id}")
                )

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Error processing file_id {file_id}: {e}")
                )
