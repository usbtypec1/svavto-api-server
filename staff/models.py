from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = ("Staff", "AdminStaff", "StaffRegisterRequest")


class Staff(models.Model):
    id = models.BigIntegerField(primary_key=True, db_index=True, editable=True)
    full_name = models.CharField(max_length=100)
    car_sharing_phone_number = models.CharField(max_length=32)
    console_phone_number = models.CharField(max_length=32)
    banned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("staff")
        verbose_name_plural = _("staff")

    def __str__(self):
        return self.full_name


class AdminStaff(models.Model):
    id = models.BigIntegerField(primary_key=True, db_index=True, editable=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("admin staff")
        verbose_name_plural = _("admin staff list")

    def __str__(self):
        return self.name or str(self.id)


class StaffRegisterRequest(models.Model):
    staff_id = models.BigIntegerField(db_index=True, unique=True)
    full_name = models.CharField(max_length=100)
    car_sharing_phone_number = models.CharField(max_length=32)
    console_phone_number = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("staff register request")
        verbose_name_plural = _("staff register requests")

    def __str__(self):
        return self.full_name
