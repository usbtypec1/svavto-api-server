from django.db import models
from django.utils.translation import gettext_lazy as _, gettext


class WindshieldWasherHidden(models.Model):
    """One-record model to hide the windshield washer."""

    is_hidden = models.BooleanField(
        verbose_name=_("Is hidden"),
        help_text=_("Indicates if the windshield washer is hidden."),
        default=False,
    )

    def __str__(self):
        if self.is_hidden:
            return gettext("Windshield washer is hidden")
        return gettext("Windshield washer is visible")

    class Meta:
        verbose_name = _("Windshield washer hidden")
        verbose_name_plural = _("Windshield washer hidden")

    @classmethod
    def get(cls) -> bool:
        """
        Returns True if the windshield washer is hidden, False otherwise.
        """
        instance = cls.objects.first()
        if instance is not None:
            return instance.is_hidden
        return False
