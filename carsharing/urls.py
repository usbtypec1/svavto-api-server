from django.conf import settings
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("staff/", include("staff.urls")),
    path("car-washes/", include("car_washes.urls")),
    path("economics/", include("economics.urls")),
    path("shifts/", include("shifts.urls")),
    path("photo-upload/", include("photo_upload.urls")),
    path("texts/", include("texts.urls")),
    path("dry-cleaning/", include("dry_cleaning.urls")),
    path("deposits/", include("deposits.urls")),
]

if settings.ROOT_PATH:
    urlpatterns = [
        path(f'{settings.ROOT_PATH}/', include(urlpatterns))
    ]

if settings.DEBUG:
    urlpatterns.append(
        path(
            f'{settings.ROOT_PATH}silk/',
            include('silk.urls'),
            name="silk",
        ),
    )
