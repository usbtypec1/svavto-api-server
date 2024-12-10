from django.urls import include, path

from economics.views import (
    PenaltyListCreateApi,
    ServiceCostsApi,
    StaffShiftsStatisticsReportApi,
    SurchargeCreateApi,
)

reports_urlpatterns = [
    path(
        r'service-costs/',
        ServiceCostsApi.as_view(),
        name='service-costs',
    ),
    path(
        r'staff-shifts-statistics/',
        StaffShiftsStatisticsReportApi.as_view(),
        name='staff-shifts-statistics',
    ),
]

urlpatterns = [
    path(
        r'penalties/',
        PenaltyListCreateApi.as_view(),
        name='penalty-list-create',
    ),
    path(r'surcharges/', SurchargeCreateApi.as_view(), name='surcharge-create'),
    path(r'reports/', include(reports_urlpatterns)),
]
