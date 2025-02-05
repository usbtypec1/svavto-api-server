import math

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from car_washes.models import CarWash, CarWashService
from staff.models import Staff

__all__ = (
    'Shift',
    'CarToWash',
    'CarToWashAdditionalService',
    'AvailableDate',
    'ShiftFinishPhoto',
)


class AvailableDate(models.Model):
    month = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                limit_value=1, message='Month must be at least 1'
            ),
            MaxValueValidator(
                limit_value=12,
                message='Month cannot be greater than 12',
            ),
        ],
        verbose_name=_('month'),
    )
    year = models.PositiveSmallIntegerField(verbose_name=_('year'))

    class Meta:
        verbose_name = _('available date')
        verbose_name_plural = _('available dates')
        unique_together = ('month', 'year')
        ordering = ('year', 'month')

    def __str__(self):
        return f'{self.year}-{self.month}'


class Shift(models.Model):

    class Type(models.TextChoices):
        REGULAR = 'regular', _('regular shift')
        TEST = 'test', _('test shift')
        EXTRA = 'extra', _('extra shift')

    staff = models.ForeignKey(
        Staff,
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
    car_wash = models.ForeignKey(
        CarWash,
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


class ShiftFinishPhoto(models.Model):
    shift = models.ForeignKey(
        to=Shift,
        related_name='finish_photos',
        on_delete=models.CASCADE,
        verbose_name=_('shift'),
    )
    file_id = models.CharField(
        max_length=255,
        verbose_name=_('file id'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
    )

    class Meta:
        verbose_name = _('shift finish photo')
        verbose_name_plural = _('shift finish photos')


class CarToWash(models.Model):
    class CarType(models.TextChoices):
        COMFORT = 'comfort', _('comfort')
        BUSINESS = 'business', _('business')
        VAN = 'van', _('van')

    class WashType(models.TextChoices):
        PLANNED = 'planned', _('planned')
        URGENT = 'urgent', _('urgent')

    number = models.CharField(
        max_length=20,
        verbose_name=_('car number'),
    )
    car_wash = models.ForeignKey(
        CarWash,
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('car wash'),
    )
    shift = models.ForeignKey(
        Shift,
        on_delete=models.CASCADE,
        verbose_name=_('shift'),
    )
    car_class = models.CharField(
        max_length=16,
        choices=CarType.choices,
        verbose_name=_('car class'),
    )
    wash_type = models.CharField(
        max_length=16,
        choices=WashType.choices,
        verbose_name=_('wash type'),
    )
    windshield_washer_refilled_bottle_percentage = (
        models.PositiveSmallIntegerField()
    )
    transfer_price = models.PositiveIntegerField(
        help_text=_('price of car transfer at the moment')
    )
    comfort_class_car_washing_price = models.PositiveIntegerField(
        help_text=_('price of comfort class car washing at the moment')
    )
    business_class_car_washing_price = models.PositiveIntegerField(
        help_text=_('price of business class car washing at the moment')
    )
    van_washing_price = models.PositiveIntegerField(
        help_text=_('price of van washing at the moment')
    )
    windshield_washer_price_per_bottle = models.PositiveIntegerField(
        help_text=_('price of windshield washer per bottle at the moment')
    )
    created_at = models.DateTimeField()

    class Meta:
        verbose_name = _('car to wash')
        verbose_name_plural = _('cars to wash')
        unique_together = ('number', 'shift')

    def __str__(self):
        return _('car number: %(number)s') % {'number': self.number}

    @property
    def washing_price(self) -> int:
        if self.car_class == self.CarType.COMFORT:
            return self.comfort_class_car_washing_price
        if self.car_class == self.CarType.BUSINESS:
            return self.business_class_car_washing_price
        if self.car_class == self.CarType.VAN:
            return self.van_washing_price
        raise ValueError(_('unknown car class'))

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
        return (self.windshield_washer_price_per_bottle *
                self.windshield_washer_refilled_bottle_count)

    @property
    def is_windshield_washer_refilled(self) -> bool:
        return self.windshield_washer_refilled_bottle_count > 0


class CarToWashAdditionalService(models.Model):
    car = models.ForeignKey(
        to=CarToWash,
        on_delete=models.CASCADE,
        related_name='additional_services',
        verbose_name=_('car to wash'),
    )
    service = models.ForeignKey(
        to=CarWashService,
        on_delete=models.CASCADE,
        verbose_name=_('additional service'),
    )
    price = models.PositiveIntegerField(
        verbose_name=_('price'),
        help_text=_('price of additional service at the moment')
    )
    count = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('count'),
    )

    class Meta:
        verbose_name = _('additional service')
        verbose_name_plural = _('additional services')
        unique_together = ('car', 'service')

    @property
    def total_price(self) -> int:
        return self.price * self.count
