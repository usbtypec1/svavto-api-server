from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from car_washes.models import CarWash
from staff.models import Staff

__all__ = ('Shift',)


class Shift(models.Model):

    class Type(models.TextChoices):
        REGULAR = 'regular', _('regular shift')
        TEST = 'test', _('test shift')
        EXTRA = 'extra', _('extra shift')

    staff = models.ForeignKey(
        to=Staff,
        on_delete=models.CASCADE,
        verbose_name=_('staff'),
    )
    date = models.DateField(
        verbose_name=_('date'),
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('started at'),
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('finished at'),
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('confirmed at'),
    )
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('rejected at'),
    )
    car_wash = models.ForeignKey(
        to=CarWash,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('car wash'),
    )
    is_extra = models.BooleanField(
        default=False,
        verbose_name=_('is extra shift'),
    )
    is_test = models.BooleanField(
        default=False,
        verbose_name=_('is test shift'),
    )
    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        default=timezone.now,
    )

    class Meta:
        verbose_name = _('shift')
        verbose_name_plural = _('shifts')
        unique_together = ('staff', 'date', 'is_test')

    def __str__(self):
        return f'{self.date:%d.%m.%Y} - {self.staff}'

    @property
    def is_started(self) -> bool:
        return self.started_at is not None

    @property
    def is_finished(self) -> bool:
        return self.finished_at is not None

    @property
    def type(self) -> Type:
        if self.is_test:
            return self.Type.TEST
        if self.is_extra:
            return self.Type.EXTRA
        return self.Type.REGULAR
