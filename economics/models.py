from django.db import models

from staff.models import Staff

__all__ = ('Penalty', 'Surcharge')


class Penalty(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Surcharge(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
