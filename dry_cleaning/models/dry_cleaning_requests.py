from django.db import models
from django.utils.translation import gettext, gettext_lazy as _

from shifts.models.shifts import Shift


class DryCleaningRequest(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 1, _('Pending')
        APPROVED = 2, _('Approved')
        REJECTED = 3, _('Rejected')

    shift = models.ForeignKey(
        to=Shift,
        on_delete=models.CASCADE,
        related_name='dry_cleaning_requests',
        verbose_name=_('Shift'),
    )
    car_number = models.CharField(
        max_length=16,
        verbose_name=_('Car number'),
    )
    status = models.PositiveSmallIntegerField(
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Status'),
    )
    response_comment = models.TextField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name=_('Response comment'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Dry cleaning request')
        verbose_name_plural = _('Dry cleaning requests')

    def __str__(self):
        return gettext('Car number %(car_number)s - shift %(shift_date)s') % {
            'car_number': self.car_number,
            'shift_date': self.shift.date,
        }
