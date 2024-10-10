from django.db import models

from performers.models import Performer

__all__ = ('Penalty',)


class Penalty(models.Model):
    performer = models.ForeignKey(Performer, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
