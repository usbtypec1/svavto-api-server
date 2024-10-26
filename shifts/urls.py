from django.urls import path

from shifts.views import ShiftDateStaffListApi, StaffShiftConfirmationSendApi

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
]
