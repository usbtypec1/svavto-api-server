from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from car_washes.models import CarWash
from shifts.models import Shift
from staff.models import Staff

__all__ = (
    'Penalty',
    'Surcharge',
    'StaffServicePrice',
    'CarWashPenalty',
    'CarWashSurcharge',
)


class CarWashPenalty(models.Model):
    car_wash = models.ForeignKey(
        to=CarWash,
        on_delete=models.CASCADE,
        related_name='penalties',
    )
    reason = models.TextField(max_length=1024)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('car wash penalty')
        verbose_name_plural = _('car wash penalties')

    def __str__(self):
        return self.reason


class CarWashSurcharge(models.Model):
    car_wash = models.ForeignKey(
        to=CarWash,
        on_delete=models.CASCADE,
        related_name='surcharges',
    )
    reason = models.TextField(max_length=1024)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('car wash surcharge')
        verbose_name_plural = _('car wash surcharges')

    def __str__(self):
        return self.reason


class Penalty(models.Model):
    class Consequence(models.TextChoices):
        DISMISSAL = 'dismissal', _('dismissal')
        WARN = 'warn', _('warn')

    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    consequence = models.CharField(
        max_length=255,
        choices=Consequence.choices,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('penalty')
        verbose_name_plural = _('penalties')

    def __str__(self):
        return self.reason


class Surcharge(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('surcharge')
        verbose_name_plural = _('surcharges')

    def __str__(self):
        return self.reason


class StaffServicePrice(models.Model):
    class ServiceType(models.TextChoices):
        COMFORT_CLASS_CAR_TRANSFER = (
            'comfort_class_car_transfer',
            _('comfort class car transfer'),
        )
        BUSINESS_CLASS_CAR_TRANSFER = (
            'business_class_car_transfer',
            _('business class car transfer'),
        )
        VAN_TRANSFER = 'van_transfer', _('van transfer')
        CAR_TRANSPORTER_EXTRA_SHIFT = (
            'car_transporter_extra_shift',
            _('car transporter extra shift'),
        )
        URGENT_CAR_WASH = 'urgent_wash', _('urgent wash')
        ITEM_DRY_CLEAN = 'item_dry_clean', _('item dry clean')
        UNDER_PLAN_PLANNED_CAR_TRANSFER = (
            'under_plan_planned_car_transfer',
            _('under plan planned car transfer')
        )

    service = models.CharField(
        max_length=255,
        choices=ServiceType.choices,
        unique=True,
    )
    price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('staff service price')
        verbose_name_plural = _('staff service prices')

    def __str__(self):
        return self.get_service_display()
