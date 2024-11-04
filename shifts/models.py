from django.db import models

from car_washes.models import CarWash
from staff.models import Staff

__all__ = ('Shift', 'CarToWash', 'CarToWashAdditionalService')


class Shift(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    confirmed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    car_wash = models.ForeignKey(
        CarWash,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )
    is_extra = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'shift'
        verbose_name_plural = 'shifts'
        unique_together = ('staff', 'date')

    @property
    def is_started(self) -> bool:
        return self.started_at is not None

    @property
    def is_finished(self) -> bool:
        return self.finished_at is not None

    @property
    def is_confirmed(self) -> bool:
        return self.confirmed_at is not None


class CarToWash(models.Model):
    class CarType(models.TextChoices):
        COMFORT = 'comfort'
        BUSINESS = 'business'
        VAN = 'van'

    class WashType(models.TextChoices):
        PLANNED = 'planned'
        URGENT = 'urgent'

    number = models.CharField(max_length=20)
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

    class Meta:
        verbose_name = 'car to wash'
        verbose_name_plural = 'cars to wash'
        unique_together = ('number', 'shift')

    def __str__(self):
        return f'Гос.номер: {self.number}'


class CarToWashAdditionalService(models.Model):
    car = models.ForeignKey(CarToWash, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    count = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = 'additional service'
        verbose_name_plural = 'additional services'

    def __str__(self):
        return self.name
