from django.db import models

__all__ = ('CarWash',)


class CarWash(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'car wash'
        verbose_name_plural = 'car washes'

    def __str__(self):
        return self.name

