from django.db import models
from django.db.models.constraints import CheckConstraint
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from staff.models import Staff


class FineDepositException(models.Model):
    staff = models.ForeignKey(
        to=Staff,
        on_delete=models.CASCADE,
        verbose_name=_("Staff"),
    )
    from_date = models.DateField(
        verbose_name=_("From date"),
        default=timezone.now,
    )
    to_date = models.DateField(
        default=timezone.now,
        verbose_name=_("To date"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    class Meta:
        verbose_name = _("Fine deposit exception")
        verbose_name_plural = _("Fine deposit exceptions")
        constraints = (
            CheckConstraint(
                check=models.Q(from_date__lte=models.F("to_date")),
                name="fine_deposit_exception_from_date_less_than_to_date",
                violation_error_message=_(
                    "From date must be less than to date.",
                ),
            ),
        )


class RoadAccidentDepositException(models.Model):
    staff = models.ForeignKey(
        to=Staff,
        on_delete=models.CASCADE,
        verbose_name=_("Staff"),
    )
    from_date = models.DateField(
        verbose_name=_("From date"),
    )
    to_date = models.DateField(verbose_name=_("To date"))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    class Meta:
        verbose_name = _("Road accident deposit exception")
        verbose_name_plural = _("Road accident deposit exceptions")
        constraints = (
            CheckConstraint(
                check=models.Q(from_date__lte=models.F("to_date")),
                name=(
                    "road_accident_deposit_exception_from_date_less_than_to_date"
                ),
                violation_error_message=_(
                    "From date must be less than to date.",
                ),
            ),
        )
