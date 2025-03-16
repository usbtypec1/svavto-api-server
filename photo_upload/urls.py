from django.urls import path

from photo_upload.views import PhotoUploadApi


urlpatterns = [
    path("", PhotoUploadApi.as_view(), name="photo_upload"),
]
