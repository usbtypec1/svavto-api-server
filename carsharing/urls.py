from django.conf import settings
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path(f"{settings.ROOT_PATH}admin/", admin.site.urls),
    path(f"{settings.ROOT_PATH}staff/", include("staff.urls")),
    path(f"{settings.ROOT_PATH}car-washes/", include("car_washes.urls")),
    path(f"{settings.ROOT_PATH}economics/", include("economics.urls")),
    path(f"{settings.ROOT_PATH}shifts/", include("shifts.urls")),
    path(f"{settings.ROOT_PATH}photo-upload/", include("photo_upload.urls")),
    path(f"{settings.ROOT_PATH}texts/", include("texts.urls")),
    path(f"{settings.ROOT_PATH}dry-cleaning/", include("dry_cleaning.urls")),
]

if settings.DEBUG:
    urlpatterns.append(
        path(
            f'{settings.ROOT_PATH}silk/',
            include('silk.urls'),
            name="silk",
        ),
    )
