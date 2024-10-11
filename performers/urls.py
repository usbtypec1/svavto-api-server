from django.urls import path

from performers.views import PerformerListCreateApi, PerformerRetrieveUpdateApi

urlpatterns = [
    path(r'', PerformerListCreateApi.as_view(), name='performer-create'),
    path(
        r'<int:telegram_id>/',
        PerformerRetrieveUpdateApi.as_view(),
        name='performer-retrieve',
    ),
]
