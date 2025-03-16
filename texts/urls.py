from django.urls import path

from texts.views import TextRetrieveApi


urlpatterns = [
    path(r"", TextRetrieveApi.as_view(), name="text-retrieve"),
]
