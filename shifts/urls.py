from django.urls import include, path
from rest_framework.routers import DefaultRouter

from shifts.views import (
    AvailableDateApi,
    CarToWashCreateApi,
    CarToWashListApi,
    CarsToWashCountByEachStaffApi,
    CarsWithoutWindshieldWasherApi,
    CurrentShiftCarWashUpdateApi,
    RetrieveUpdateCarsToWashApi,
    ShiftConfirmApi, ShiftExtraCreateApi,
    ShiftFinishApi,
    ShiftListApi,
    ShiftListForSpecificDateApi,
    ShiftRegularCreateApi,
    ShiftRejectApi, ShiftRetrieveApi,
    ShiftRetrieveDeleteApi,
    ShiftStartApi,
    ShiftTestCreateApi,
    StaffCurrentShiftRetrieveApi,
    StaffReportPeriodsListApi,
    StaffShiftListApi,
    ShiftListApiV2, DeadSoulsApi, StaffShiftsMonthListApi,
)


router = DefaultRouter()
router.register(
    r'available-dates',
    AvailableDateApi,
    basename='available-date',
)

app_name = 'shifts'
urlpatterns = [
    path(
        'v2/',
        ShiftListApiV2.as_view(),
        name='v2-list',
    ),
    path(
        r'',
        ShiftListApi.as_view(),
        name='list',
    ),
    path(
        r'reject/',
        ShiftRejectApi.as_view(),
        name='reject',
    ),
    path(
        r'dead-souls/',
        DeadSoulsApi.as_view(),
        name='dead-souls',
    ),
    path(
        r'report-periods/staff/<int:staff_id>/',
        StaffReportPeriodsListApi.as_view(),
        name='staff-report-periods'
    ),
    path(
        'specific-date/',
        ShiftListForSpecificDateApi.as_view(),
        name='specific-date',
    ),
    path(
        r'staff/<int:staff_id>/months/',
        StaffShiftsMonthListApi.as_view(),
        name='staff-shifts-month-list',
    ),
    path(
        r'create/',
        ShiftRegularCreateApi.as_view(),
        name='create-regular',
    ),
    path(
        r'confirm/',
        ShiftConfirmApi.as_view(),
        name='confirm',
    ),
    path(
        r'create/test/',
        ShiftTestCreateApi.as_view(),
        name='create-test',
    ),
    path(
        r'create/extra/',
        ShiftExtraCreateApi.as_view(),
        name='create-extra',
    ),
    path(
        r'<int:shift_id>/',
        ShiftRetrieveDeleteApi.as_view(),
        name='delete',
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
    path(r'<int:shift_id>/', ShiftRetrieveApi.as_view(), name='retrieve'),
    path(r'', include(router.urls)),
]
