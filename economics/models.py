from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from car_washes.models import CarWash
from core.models import SingleRowModelMixin
from shifts.models import Shift
from staff.models import Staff


class CarWashPenalty(models.Model):
    car_wash = models.ForeignKey(
        to=CarWash,
        on_delete=models.CASCADE,
        related_name="penalties",
        verbose_name=_("Car wash"),
    )
    reason = models.TextField(max_length=1024, verbose_name=_("Reason"))
    amount = models.PositiveIntegerField(verbose_name=_("Amount"))
    date = models.DateField(verbose_name=_("Date"))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    class Meta:
        verbose_name = _("car wash penalty")
        verbose_name_plural = _("car wash penalties")

    def __str__(self):
        return self.reason


class CarWashSurcharge(models.Model):
    car_wash = models.ForeignKey(
        to=CarWash,
        on_delete=models.CASCADE,
        related_name="surcharges",
        verbose_name=_("Car wash"),
    )
    reason = models.TextField(
        max_length=1024,
        verbose_name=_("Reason"),
    )
    amount = models.PositiveIntegerField(verbose_name=_("Amount"))
    date = models.DateField(verbose_name=_("Date"))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    class Meta:
        verbose_name = _("car wash surcharge")
        verbose_name_plural = _("car wash surcharges")

    def __str__(self):
        return self.reason


class CarTransporterPenalty(models.Model):
    class Consequence(models.TextChoices):
        DISMISSAL = "dismissal", _("dismissal")
        WARN = "warn", _("warn")

    staff = models.ForeignKey(
        to=Staff,
        on_delete=models.CASCADE,
        related_name="penalties",
        verbose_name=_("Staff"),
    )
    date = models.DateField(default=timezone.localdate, verbose_name=_("Date"))
    reason = models.CharField(max_length=255, verbose_name=_("Reason"))
    amount = models.PositiveIntegerField(verbose_name=_("Amount"))
    consequence = models.CharField(
        max_length=255,
        choices=Consequence.choices,
        null=True,
        blank=True,
        verbose_name=_("Consequence"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Car transporter penalty")
        verbose_name_plural = _("Car transporter penalties")

    def __str__(self):
        return self.reason


class PenaltyPhoto(models.Model):
    penalty = models.ForeignKey(
        to=CarTransporterPenalty,
        on_delete=models.CASCADE,
        verbose_name=_("Penalty"),
    )
    photo_url = models.URLField(verbose_name=_("Photo URL"))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    class Meta:
        verbose_name = _("penalty photo")
        verbose_name_plural = _("penalty photos")


class CarTransporterSurcharge(models.Model):
    staff = models.ForeignKey(
        to=Staff,
        on_delete=models.CASCADE,
        related_name="surcharges",
        verbose_name=_("Staff"),
    )
    date = models.DateField(
        default=timezone.localdate,
        verbose_name=_("Date"),
    )
    reason = models.CharField(max_length=255, verbose_name=_("Reason"))
    amount = models.PositiveIntegerField(verbose_name=_("Amount"))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    class Meta:
        verbose_name = _("Car transporter surcharge")
        verbose_name_plural = _("Car transporter surcharges")

    def __str__(self):
        return self.reason


class CarTransporterAndWasherServicePrices(SingleRowModelMixin, models.Model):
    comfort_class_car_transfer = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Comfort class car transfer"),
    )
    business_class_car_transfer = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Business class car transfer"),
    )
    van_transfer = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Van transfer"),
    )
    urgent_car_transfer = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Urgent car transfer"),
    )
    item_dry_cleaning = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Item dry cleaning"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Car transporter and washer service price")
        verbose_name_plural = _("Car transporter and washer service prices")


class CarTransporterServicePrices(SingleRowModelMixin, models.Model):
    comfort_class_car_transfer = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Comfort class car transfer"),
    )
    business_class_car_transfer = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Business class car transfer"),
    )
    van_transfer = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Van transfer"),
    )
    extra_shift = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Extra shift"),
    )
    urgent_car_transfer = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Urgent car transfer"),
    )
    item_dry_cleaning = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Item dry cleaning"),
    )
    under_plan_planned_car_transfer = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Under plan planned car transfer"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Car transporter service price")
        verbose_name_plural = _("Car transporter service prices")
