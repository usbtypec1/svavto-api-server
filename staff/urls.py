from django.urls import path

from staff.views import (
    StaffListCreateApi,
    PerformerRetrieveUpdateApi,
    StaffUpdateAvailableDatesApi,
)

urlpatterns = [
    path(r'', StaffListCreateApi.as_view(), name='staff-create'),
    path(
        r'<int:staff_id>/',
        PerformerRetrieveUpdateApi.as_view(),
        name='staff-retrieve',
    ),
    path(
        r'<int:staff_id>/available-dates/',
        StaffUpdateAvailableDatesApi.as_view(),
        name='staff-available-dates',
    ),
]
