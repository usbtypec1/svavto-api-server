from django.db import models

__all__ = ('CarWash', 'CarWashServicePrice')


class CarWash(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'car wash'
        verbose_name_plural = 'car washes'

    def __str__(self):
        return self.name


class CarWashServicePrice(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    car_wash = models.ForeignKey(
        to=CarWash,
        on_delete=models.CASCADE,
    )
    service_name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'car wash service price'
        verbose_name_plural = 'car wash service prices'

    def __str__(self):
        return f'{self.service_name}'
