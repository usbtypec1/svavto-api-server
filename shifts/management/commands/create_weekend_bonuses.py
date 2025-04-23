import datetime

from django.core.management import BaseCommand
from django.db.models import Count

from economics.models import CarTransporterSurcharge
from shifts.models import Shift


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'date', type=datetime.date.fromisoformat,
            help='ISOformat - YYYY-MM-DD',
        )

    def handle(self, *args, **options):
        date: datetime.date = options['date']
        values = (
            Shift.objects
            .filter(date=date, is_test=False, is_extra=False)
            .annotate(cars_count=Count('cartowash'))
            .filter(cars_count__gte=4)
            .values('cars_count', 'staff_id')
        )
        for value in values:
            CarTransporterSurcharge.objects.create(
                staff_id=value['staff_id'],
                date=date,
                reason='Премия за выход на смену в выходные дни',
                amount=300,
            )

