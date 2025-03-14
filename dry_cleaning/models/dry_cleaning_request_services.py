from django.db import models
from django.utils.translation import gettext_lazy as _

from car_washes.models import CarWashService
from dry_cleaning.models.dry_cleaning_requests import DryCleaningRequest


class DryCleaningRequestService(models.Model):
    request = models.ForeignKey(
        to=DryCleaningRequest,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name=_('Dry cleaning request'),
    )
    service = models.ForeignKey(
        to=CarWashService,
        on_delete=models.CASCADE,
        verbose_name=_('Car wash service'),
    )
    count = models.PositiveSmallIntegerField(verbose_name=_('Count'))

    class Meta:
        verbose_name = _('Dry cleaning request service')
        verbose_name_plural = _('Dry cleaning request services')
        constraints = [
            models.UniqueConstraint(
                fields=('request', 'service'),
                name='unique_dry_cleaning_request_service',
            ),
        ]
