from uuid import uuid4

from django.db import models
from django.utils.translation.trans_null import gettext_lazy as _

__all__ = ('CarWash', 'CarWashService', 'CarWashServicePrice')


class CarWash(models.Model):
    """
    Represents a car wash.
    Can have multiple services and specific prices for each service.
    """
    name = models.CharField(max_length=100, unique=True)
    comfort_class_car_transfer_price = models.PositiveIntegerField()
    business_class_car_transfer_price = models.PositiveIntegerField()
    van_transfer_price = models.PositiveIntegerField()
    windshield_washer_price_per_bottle = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('car wash')
        verbose_name_plural = _('car washes')

    def __str__(self):
        return self.name


class CarWashService(models.Model):
    """
    Represents a possible service that could be provided by car wash.
    """
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=64)
    is_countable = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('car wash service')
        verbose_name_plural = _('car wash services')

    def __str__(self):
        if self.parent is not None:
            return f'{self.parent} - {self.name}'
        return f'{self.name}'


class CarWashServicePrice(models.Model):
    """
    Represents a service that can provided by a car wash and its price.
    """
    car_wash = models.ForeignKey(
        CarWash,
        on_delete=models.CASCADE,
        related_name='prices',
    )
    service = models.ForeignKey(
        CarWashService,
        on_delete=models.CASCADE,
        related_name='prices',
    )
    price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('car wash service price')
        verbose_name_plural = _('car wash service prices')
