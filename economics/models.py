from typing import Final

from django.db import models
from django.utils.translation.trans_null import gettext_lazy as _

from staff.models import Staff

__all__ = ('Penalty', 'Surcharge', 'StaffServicePrice')


class Penalty(models.Model):
    class Consequence(models.TextChoices):
        DISMISSAL = 'dismissal', _('dismissal')
        WARN = 'warn', _('warn')

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
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
        verbose_name = 'penalty'
        verbose_name_plural = 'penalties'

    def __str__(self):
        return self.reason


class Surcharge(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'surcharge'
        verbose_name_plural = 'surcharges'

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

    service = models.CharField(
        max_length=255,
        choices=ServiceType.choices,
        unique=True,
    )
    price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_service_display()
