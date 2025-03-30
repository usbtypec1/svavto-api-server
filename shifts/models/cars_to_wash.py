import math

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from car_washes.models import CarWash
from shifts.models.shifts import Shift


__all__ = ("CarToWash",)


class CarToWash(models.Model):
    class CarType(models.TextChoices):
        COMFORT = "comfort", _("comfort")
        BUSINESS = "business", _("business")
        VAN = "van", _("van")

    class WashType(models.TextChoices):
        PLANNED = "planned", _("planned")
        URGENT = "urgent", _("urgent")

    class WindshieldWasherType(models.TextChoices):
        WATER = "water", _("Water")
        ANTIFREEZE = "antifreeze", _("Antifreeze")

    number = models.CharField(
        max_length=20,
        verbose_name=_("car number"),
    )
    car_wash = models.ForeignKey(
        CarWash,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
        verbose_name=_("car wash"),
    )
    shift = models.ForeignKey(
        Shift,
        on_delete=models.CASCADE,
        verbose_name=_("shift"),
    )
    car_class = models.CharField(
        max_length=16,
        choices=CarType.choices,
        verbose_name=_("car class"),
    )
    wash_type = models.CharField(
        max_length=16,
        choices=WashType.choices,
        verbose_name=_("wash type"),
    )
    windshield_washer_type = models.CharField(
        max_length=16,
        choices=WindshieldWasherType.choices,
        default=WindshieldWasherType.ANTIFREEZE,
        verbose_name=_("Windshield washer type"),
    )
    windshield_washer_refilled_bottle_percentage = (
        models.PositiveSmallIntegerField())
    transfer_price = models.PositiveIntegerField(
        help_text=_("price of car transfer at the moment")
    )
    comfort_class_car_washing_price = models.PositiveIntegerField(
        help_text=_("price of comfort class car washing at the moment")
    )
    business_class_car_washing_price = models.PositiveIntegerField(
        help_text=_("price of business class car washing at the moment")
    )
    van_washing_price = models.PositiveIntegerField(
        help_text=_("price of van washing at the moment")
    )
    windshield_washer_price_per_bottle = models.PositiveIntegerField(
        help_text=_("price of windshield washer per bottle at the moment")
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("car to wash")
        verbose_name_plural = _("cars to wash")
        unique_together = ("number", "shift")

    def __str__(self):
        return _("car number: %(number)s") % {"number": self.number}

    @property
    def washing_price(self) -> int:
        if self.car_class == self.CarType.COMFORT:
            return self.comfort_class_car_washing_price
        if self.car_class == self.CarType.BUSINESS:
            return self.business_class_car_washing_price
        if self.car_class == self.CarType.VAN:
            return self.van_washing_price
        raise ValueError(_("unknown car class"))

    @property
    def windshield_washer_refilled_bottle_count(self) -> int:
        """
        Calculates the number of bottles needed to refill a windshield washer
        based on the given percentage of a single bottle's capacity.

        Any amount of liquid up to 100% of a bottle's capacity is considered as
        one bottle.

        For example, 101% of a bottle's capacity is considered as 2 bottles.
        50% of a bottle's capacity is considered as 1 bottle.
        0% of a bottle's capacity is considered as 0 bottles.

        Returns:
            int: Total number of bottles needed to meet the given percentage.
        """
        return math.ceil(
            self.windshield_washer_refilled_bottle_percentage / 100
        )

    @property
    def windshield_washer_price(self) -> int:
        return (
                self.windshield_washer_price_per_bottle
                * self.windshield_washer_refilled_bottle_count
        )

    @property
    def is_windshield_washer_not_refilled(self) -> bool:
        """
        Check if the windshield washer is not refilled.
        Water is not considered as a windshield washer.
        """
        return (
                self.windshield_washer_type ==
                self.WindshieldWasherType.ANTIFREEZE
                and self.windshield_washer_refilled_bottle_percentage == 0
        )
