from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from car_washes.models import CarWash, CarWashService
from staff.models import Staff

__all__ = ('Shift', 'CarToWash', 'CarToWashAdditionalService', 'AvailableDate')


class AvailableDate(models.Model):
    month = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1, message='Month must be at least 1'
            ),
            MaxValueValidator(
                limit_value=12,
                message='Month cannot be greater than 12',
            ),
        ]
    )
    year = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = 'available date'
        verbose_name_plural = 'available dates'
        unique_together = ('month', 'year')
        ordering = ('year', 'month')


class Shift(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    car_wash = models.ForeignKey(
        CarWash,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )
    statement_photo_file_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    service_app_photo_file_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    is_extra = models.BooleanField(default=False)
    created_at = models.DateTimeField()

    class Meta:
        verbose_name = 'shift'
        verbose_name_plural = 'shifts'
        unique_together = ('staff', 'date', 'is_extra')

    def __str__(self):
        return f'{self.staff.full_name} - {self.date}'

    def full_clean(
        self, exclude=None, validate_unique=True, validate_constraints=True
    ):
        finish_requirements = (
            self.is_finished,
            self.has_statement_photo_file_id,
            self.has_service_app_photo_file_id,
        )
        if any(finish_requirements) and not all(finish_requirements):
            raise ValidationError(
                message=_('All finish requirements are not satisfied'),
                code='finish_requirements_not_satisfied',
            )

        super().full_clean(exclude, validate_unique, validate_constraints)

    @property
    def is_started(self) -> bool:
        return self.started_at is not None

    @property
    def is_finished(self) -> bool:
        return self.finished_at is not None

    @property
    def has_statement_photo_file_id(self) -> bool:
        return self.statement_photo_file_id is not None

    @property
    def has_service_app_photo_file_id(self) -> bool:
        return self.service_app_photo_file_id is not None


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
    transfer_price = models.PositiveIntegerField(
        help_text=_('Price of car transfer at the moment')
    )
    comfort_class_car_washing_price = models.PositiveIntegerField(
        help_text=_('Price of comfort class car washing at the moment')
    )
    business_class_car_washing_price = models.PositiveIntegerField(
        help_text=_('Price of business class car washing at the moment')
    )
    van_washing_price = models.PositiveIntegerField(
        help_text=_('Price of van washing at the moment')
    )
    windshield_washer_price_per_bottle = models.PositiveIntegerField(
        help_text=_('Price of windshield washer per bottle at the moment')
    )
    created_at = models.DateTimeField()

    class Meta:
        verbose_name = 'car to wash'
        verbose_name_plural = 'cars to wash'
        unique_together = ('number', 'shift')

    def __str__(self):
        return f'Гос.номер: {self.number}'


class CarToWashAdditionalService(models.Model):
    car = models.ForeignKey(CarToWash, on_delete=models.CASCADE)
    service = models.ForeignKey(CarWashService, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(
        help_text=_('Price of additional service at the moment')
    )
    count = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'additional service'
        verbose_name_plural = 'additional services'
        unique_together = ('car', 'service')
