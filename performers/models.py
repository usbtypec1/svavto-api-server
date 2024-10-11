from django.db import models

__all__ = ('Performer',)


class Performer(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=100)
    car_sharing_phone_number = models.CharField(max_length=16)
    console_phone_number = models.CharField(max_length=16)
    banned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_banned(self) -> bool:
        return self.banned_at is not None
