from django.db import models
from django.utils.translation import gettext_lazy as _

from car_washes.models import CarWashService
from shifts.models.cars_to_wash import CarToWash

__all__ = ("CarToWashAdditionalService",)


class CarToWashAdditionalService(models.Model):
    car = models.ForeignKey(
        to=CarToWash,
        on_delete=models.CASCADE,
        related_name="additional_services",
        verbose_name=_("car to wash"),
    )
    service = models.ForeignKey(
        to=CarWashService,
        on_delete=models.CASCADE,
        verbose_name=_("additional service"),
    )
    price = models.PositiveIntegerField(
        verbose_name=_("price"),
        help_text=_("price of additional service at the moment"),
    )
    count = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_("count"),
    )

    class Meta:
        verbose_name = _("additional service")
        verbose_name_plural = _("additional services")
        unique_together = ("car", "service")

    @property
    def total_price(self) -> int:
        return self.price * self.count
