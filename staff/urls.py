from django.urls import path

from staff.views import (
    AdminStaffListApi,
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
    path('admins/', AdminStaffListApi.as_view(), name='admin-staff-list'),
]
