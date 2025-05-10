from django.contrib.admin import site
from django.conf import settings


if settings.APP_NAME:
    site.site_header = f"{settings.APP_NAME} admin"
    site.site_title = f"{settings.APP_NAME} admin"
    site.index_title = f"{settings.APP_NAME} administration"


class SingleRowMixin:
    """
    Mixin to restrict the admin interface to a single row.
    """

    def has_add_permission(self, request):
        return not self.model.objects.exists()
