from django.db import models

from car_washes.models import CarWash
from staff.models import Staff

__all__ = ('Shift', 'CarToWash', 'CarToWashAdditionalService')


class Shift(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    is_confirmed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    car_wash = models.ForeignKey(
        CarWash,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class CarToWash(models.Model):
    class CarType(models.TextChoices):
        COMFORT = 'comfort'
        BUSINESS = 'business'
        VAN = 'van'

    class WashType(models.TextChoices):
        PLANNED = 'planned'
        URGENT = 'urgent'

    number = models.CharField(max_length=20, choices=CarType.choices)
    car_wash = models.ForeignKey(
        CarWash,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    car_class = models.CharField(max_length=16, choices=CarType.choices)
    wash_type = models.CharField(max_length=16, choices=WashType.choices)
    windshield_washer_refilled_bottle_percentage = (
        models.PositiveSmallIntegerField()
    )
    created_at = models.DateTimeField(auto_now_add=True)


class CarToWashAdditionalService(models.Model):
    car = models.ForeignKey(CarToWash, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    count = models.PositiveSmallIntegerField()
