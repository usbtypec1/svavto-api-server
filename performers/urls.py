from django.urls import path

from performers.views import PerformerCreateApi, PerformerRetrieveApi

urlpatterns = [
    path(r'', PerformerCreateApi.as_view(), name='performer-create'),
    path(
        r'<int:telegram_id>/',
        PerformerRetrieveApi.as_view(),
        name='performer-retrieve',
    ),
]
