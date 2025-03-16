from django.urls import path

from staff.views import (
    AdminStaffListApi,
    StaffListApi,
    StaffRegisterRequestAcceptApi,
    StaffRegisterRequestListCreateApi,
    StaffRegisterRequestRejectApi,
    StaffRetrieveUpdateApi,
)

app_name = "staff"
urlpatterns = [
    path(r"", StaffListApi.as_view(), name="list"),
    path(
        r"<int:staff_id>/",
        StaffRetrieveUpdateApi.as_view(),
        name="staff-retrieve",
    ),
    path(
        r"register-requests/",
        StaffRegisterRequestListCreateApi.as_view(),
        name="register-request-list-create",
    ),
    path(
        r"register-requests/accept/",
        StaffRegisterRequestAcceptApi.as_view(),
        name="register-request-accept",
    ),
    path(
        r"register-requests/reject/",
        StaffRegisterRequestRejectApi.as_view(),
        name="register-request-reject",
    ),
    path("admins/", AdminStaffListApi.as_view(), name="admin-staff-list"),
]
