from django.urls import path

from shifts.views import (
    CarToWashCreateApi, CarToWashListApi, CarsToWashCountByEachStaffApi,
    CarsWithoutWindshieldWasherApi, CurrentShiftCarWashUpdateApi,
    RetrieveUpdateCarsToWashApi, ShiftConfirmApi, ShiftDateStaffListApi,
    ShiftStartApi, StaffCurrentShiftRetrieveApi, StaffShiftListApi
)
from shifts.views.shifts.current.finish import ShiftFinishApi

app_name = 'shifts'
urlpatterns = [
    path(
        r'confirm/',
        ShiftConfirmApi.as_view(),
        name='confirm',
    ),
    path(
        r'start/',
        ShiftStartApi.as_view(),
        name='start',
    ),
    path(
        r'finish/',
        ShiftFinishApi.as_view(),
        name='finish',
    ),
    path(
        r'current/<int:staff_id>/car-washes/',
        CurrentShiftCarWashUpdateApi.as_view(),
        name='current-shift-car-wash',
    ),
    path(
        r'current/<int:staff_id>/',
        StaffCurrentShiftRetrieveApi.as_view(),
        name='current-shift',
    ),
    path(
        r'staff/<int:staff_id>/',
        StaffShiftListApi.as_view(),
    ),
    path(
        r'staff/',
        ShiftDateStaffListApi.as_view(),
        name='staff-list',
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
