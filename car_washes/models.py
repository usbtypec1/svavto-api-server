from django.db import models
from django.utils.translation.trans_null import gettext_lazy as _

__all__ = ('CarWash', 'CarWashService')


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
    car_wash = models.ForeignKey(
        to=CarWash,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=64, unique=True)
    price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('car wash service')
        verbose_name_plural = _('car wash services')

    def __str__(self):
        return f'{self.name}'
