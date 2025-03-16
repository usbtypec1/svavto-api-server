from django.db import models
from django.utils.translation import gettext_lazy as _

from dry_cleaning.models.dry_cleaning_requests import DryCleaningRequest


class DryCleaningRequestPhoto(models.Model):
    request = models.ForeignKey(
        to=DryCleaningRequest,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name=_("Dry cleaning request"),
    )
    url = models.URLField(max_length=255, verbose_name=_("url"))

    class Meta:
        verbose_name = _("Dry cleaning request photo")
        verbose_name_plural = _("Dry cleaning request photos")
