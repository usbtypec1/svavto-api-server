import sqlite3

from django.core.management.base import BaseCommand
from django.conf import settings

from shifts.models import ShiftFinishPhoto


class Command(BaseCommand):

    def handle(self, *args, **options):
        path = settings.ROOT_PATH / "photos.db"
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_id, url FROM data;")
            rows = cursor.fetchall()

        for i, (file_id, url) in enumerate(rows, start=1):
            ShiftFinishPhoto.objects.filter(file_id=file_id).update(url=url)
            self.stdout.write(
                f"[{i}/{len(rows)}] Updated file_id: {file_id} with URL: {url}\n"
            )
