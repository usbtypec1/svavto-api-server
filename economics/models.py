from django.db import models
from django.utils.translation.trans_null import gettext_lazy as _

from staff.models import Staff

__all__ = ('Penalty', 'Surcharge')


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


class Surcharge(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'surcharge'
        verbose_name_plural = 'surcharges'
