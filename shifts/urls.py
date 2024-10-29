from django.urls import path

from shifts.views import (
    ShiftDateStaffListApi,
    StaffShiftConfirmationSendApi,
    UpdateCarsToWashApi,
    CarToWashListCreateApi,
)

app_name = 'shifts'
urlpatterns = [
    path(
        r'staff/',
        ShiftDateStaffListApi.as_view(),
        name='staff-list',
    ),
    path(
        r'send-confirmation/',
        StaffShiftConfirmationSendApi.as_view(),
        name='staff-confirmation-send',
    ),
    path(
        r'cars/',
        CarToWashListCreateApi.as_view(),
        name='car-list-create',
    ),
    path(
        r'cars/<int:car_id>/',
        UpdateCarsToWashApi.as_view(),
        name='car-update',
    ),
]
