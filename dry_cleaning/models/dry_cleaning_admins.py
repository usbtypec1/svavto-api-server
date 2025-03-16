from django.db import models
from django.utils.translation import gettext_lazy as _


class DryCleaningAdmin(models.Model):
    id = models.BigIntegerField(primary_key=True, db_index=True, editable=True)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Dry cleaning admin")
        verbose_name_plural = _("Dry cleaning admins")
