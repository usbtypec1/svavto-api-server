from django.db import models

from performers.models import Performer


class Shift(models.Model):
    performer = models.ForeignKey(Performer)
