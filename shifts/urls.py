from django.urls import path

from shifts.views import (
    ShiftDateStaffListApi,
    StaffShiftConfirmationSendApi,
    RetrieveUpdateCarsToWashApi,
    CarToWashListApi,
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
        r'cars/<int:car_id>/',
        RetrieveUpdateCarsToWashApi.as_view(),
        name='car-update',
    ),
    path(
        r'cars/staff/<int:staff_id>/',
        CarToWashListApi.as_view(),
        name='car-list',
    ),
]
