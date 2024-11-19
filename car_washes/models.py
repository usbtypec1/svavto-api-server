from uuid import uuid4

from django.db import models
from django.utils.translation.trans_null import gettext_lazy as _

__all__ = ('CarWash', 'CarWashService', 'CarWashServicePrice')


class CarWash(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('car wash')
        verbose_name_plural = _('car washes')

    def __str__(self):
        return self.name


class CarWashService(models.Model):
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
        return f'{self.name}'


class CarWashServicePrice(models.Model):
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
