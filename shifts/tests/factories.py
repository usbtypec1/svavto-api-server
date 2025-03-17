import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from shifts.models import AvailableDate, Shift, CarToWash, CarToWashAdditionalService
from staff.tests.factories import StaffFactory
from car_washes.tests.factories import CarWashFactory, CarWashServiceFactory


class AvailableDateFactory(DjangoModelFactory):
    class Meta:
        model = AvailableDate
        django_get_or_create = (
            "month",
            "year",
        )

    month = factory.Faker("random_int", min=1, max=12)
    year = factory.Faker("random_int", min=2000, max=2100)


class ShiftFactory(DjangoModelFactory):
    class Meta:
        model = Shift
        django_get_or_create = (
            "staff",
            "date",
            "started_at",
            "finished_at",
            "rejected_at",
            "car_wash",
            "is_extra",
            "is_test",
            "created_at",
        )

    staff = factory.SubFactory(StaffFactory)
    date = factory.Faker("date_object")
    started_at = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    finished_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )
    confirmed_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )
    rejected_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )
    car_wash = None
    is_extra = False
    is_test = False
    created_at = factory.Faker(
        "date_time",
        tzinfo=timezone.get_current_timezone(),
    )


class TransferredCarFactory(DjangoModelFactory):
    class Meta:
        model = CarToWash

    number = factory.Faker("license_plate")
    car_wash = factory.SubFactory(CarWashFactory)
    shift = factory.SubFactory(ShiftFactory)
    car_class = factory.Iterator(CarToWash.CarType.values)
    wash_type = factory.Iterator(CarToWash.WashType.values)
    windshield_washer_type = factory.Iterator(CarToWash.WindshieldWasherType.values)
    windshield_washer_refilled_bottle_percentage = factory.Faker(
        "random_int", min=0, max=100
    )
    transfer_price = factory.Faker("random_int", min=100, max=1000)
    comfort_class_car_washing_price = factory.Faker("random_int", min=100, max=1000)
    business_class_car_washing_price = factory.Faker("random_int", min=100, max=1000)
    van_washing_price = factory.Faker("random_int", min=100, max=1000)
    windshield_washer_price_per_bottle = factory.Faker("random_int", min=10, max=100)
    created_at = factory.Faker(
        "date_time_this_year",
        before_now=True,
        after_now=False,
        tzinfo=timezone.get_current_timezone(),
    )


class TransferredCarAdditionalServiceFactory(DjangoModelFactory):
    class Meta:
        model = CarToWashAdditionalService

    car = factory.SubFactory(TransferredCarFactory)
    service = factory.SubFactory(CarWashServiceFactory)
    price = factory.Faker("random_int", min=100, max=1000)
    count = factory.Faker("random_int", min=1, max=100)
