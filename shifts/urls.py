from django.urls import path

from shifts.views import (
    ShiftDateStaffListApi,
    StaffShiftConfirmationSendApi,
    RetrieveUpdateCarsToWashApi,
    CarToWashListApi,
    StaffCurrentShiftRetrieveApi,
    CarToWashCreateApi,
    CarsToWashCountByEachStaffApi,
    CarsWithoutWindshieldWasherApi,
    CurrentShiftCarWashUpdateApi,
)

app_name = 'shifts'
urlpatterns = [
    path(
        r'current/<int:staff_id>/car-washes/',
        CurrentShiftCarWashUpdateApi.as_view(),
        name='current-shift-car-wash',
    ),
    path(
        r'staff/',
        ShiftDateStaffListApi.as_view(),
        name='staff-list',
    ),
    path(
        r'staff/<int:staff_id>/',
        StaffCurrentShiftRetrieveApi.as_view(),
        name='staff-retrieve',
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
        r'cars/',
        CarToWashCreateApi.as_view(),
        name='car-create',
    ),
    path(
        r'cars/staff/<int:staff_id>/',
        CarToWashListApi.as_view(),
        name='car-list',
    ),
    path(
        r'cars/count-by-staff/',
        CarsToWashCountByEachStaffApi.as_view(),
        name='car-count-by-staff',
    ),
    path(
        r'cars/without-windshield-washer/',
        CarsWithoutWindshieldWasherApi.as_view(),
        name='car-without-windshield-washer',
    ),
]
