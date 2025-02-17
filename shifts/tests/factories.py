import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from shifts.models import AvailableDate
from shifts.models.shifts import Shift
from staff.tests.factories import StaffFactory

__all__ = ('ShiftFactory', 'AvailableDateFactory')


class AvailableDateFactory(DjangoModelFactory):

    class Meta:
        model = AvailableDate
        django_get_or_create = (
            'month',
            'year',
        )

    month = factory.Faker('random_int', min=1, max=12)
    year = factory.Faker('random_int', min=2000, max=2100)


class ShiftFactory(DjangoModelFactory):

    class Meta:
        model = Shift
        django_get_or_create = (
            'staff',
            'date',
            'started_at',
            'finished_at',
            'rejected_at',
            'car_wash',
            'is_extra',
            'is_test',
            'created_at',
        )

    staff = factory.SubFactory(StaffFactory)
    date = factory.Faker('date_object')
    started_at = factory.Faker(
        'date_time',
        tzinfo=timezone.get_current_timezone()
    )
    finished_at = factory.Faker(
        'date_time',
        tzinfo=timezone.get_current_timezone(),
    )
    rejected_at = factory.Faker(
        'date_time',
        tzinfo=timezone.get_current_timezone(),
    )
    car_wash = None
    is_extra = False
    is_test = False
    created_at = factory.Faker(
        'date_time',
        tzinfo=timezone.get_current_timezone(),
    )
