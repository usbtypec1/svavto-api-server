from django.urls import path

from staff.views import (
    StaffListCreateApi,
    PerformerRetrieveUpdateApi,
    StaffUpdateShiftScheduleYearAndMonthApi,
)

urlpatterns = [
    path(r'', StaffListCreateApi.as_view(), name='staff-create'),
    path(
        r'<int:staff_id>/',
        PerformerRetrieveUpdateApi.as_view(),
        name='staff-retrieve',
    ),
    path(
        r'<int:staff_id>/shift-schedule-year-and-month/',
        StaffUpdateShiftScheduleYearAndMonthApi.as_view(),
        name='staff-update-shift-schedule-year-and-month',
    ),
]
