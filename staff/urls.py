from django.urls import path

from staff.views import (
    StaffListCreateApi,
    StaffRetrieveUpdateApi,
)

urlpatterns = [
    path(r'', StaffListCreateApi.as_view(), name='staff-create'),
    path(
        r'<int:staff_id>/',
        StaffRetrieveUpdateApi.as_view(),
        name='staff-retrieve',
    ),
]
