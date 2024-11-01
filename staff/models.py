from django.db import models

__all__ = ('Staff', 'StaffAvailableDate')


class Staff(models.Model):
    id = models.BigIntegerField(primary_key=True, db_index=True)
    full_name = models.CharField(max_length=100)
    car_sharing_phone_number = models.CharField(max_length=16)
    console_phone_number = models.CharField(max_length=16)
    banned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'staff'
        verbose_name_plural = 'staff'

    def __str__(self):
        return self.full_name

    @property
    def is_banned(self) -> bool:
        return self.banned_at is not None


class StaffAvailableDate(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name = 'staff available date'
        verbose_name_plural = 'staff available dates'
        unique_together = ('staff', 'month', 'year')
