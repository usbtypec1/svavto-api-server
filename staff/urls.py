from django.urls import path

from staff.views import StaffListCreateApi, PerformerRetrieveUpdateApi

urlpatterns = [
    path(r'', StaffListCreateApi.as_view(), name='staff-create'),
    path(
        r'<int:telegram_id>/',
        PerformerRetrieveUpdateApi.as_view(),
        name='staff-retrieve',
    ),
]
