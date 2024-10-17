from django.db import models

from staff.models import Staff

__all__ = ('Shift',)


class Shift(models.Model):
    performer = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
