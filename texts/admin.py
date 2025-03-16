from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from texts.models import Text


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
    search_fields = ("key", "value")
    ordering = ("key",)
    readonly_fields = ("raw_key",)

    @admin.display(description=_("Key"))
    def raw_key(self, obj: Text):
        return obj.key
