from django.db import models
from django.utils.translation import gettext_lazy as _

from shifts.models.shifts import Shift

__all__ = ("ShiftFinishPhoto",)


class ShiftFinishPhoto(models.Model):
    shift = models.ForeignKey(
        to=Shift,
        related_name="finish_photos",
        on_delete=models.CASCADE,
        verbose_name=_("shift"),
    )
    file_id = models.CharField(
        max_length=255,
        verbose_name=_("file id"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
    )

    class Meta:
        verbose_name = _("shift finish photo")
        verbose_name_plural = _("shift finish photos")
