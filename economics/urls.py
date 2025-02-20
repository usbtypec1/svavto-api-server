from django.urls import include, path

from economics.views import (
    PenaltyListCreateApi,
    ServiceCostsApi,
    StaffShiftsStatisticsReportApi,
    SurchargeCreateApi,
    CarWashPenaltyListCreateApi,
    CarWashSurchargeListCreateApi,
    CarWashSurchargeDeleteApi,
    CarWashPenaltyDeleteApi,
    CarTransporterPenaltyDeleteApi,
    CarTransporterSurchargeDeleteApi,
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

app_name = 'economics'
urlpatterns = [
    path(
        r'car-washes/penalties/',
        CarWashPenaltyListCreateApi.as_view(),
        name='car-wash-penalty-list-create',
    ),
    path(
        r'car-washes/surcharges/',
        CarWashSurchargeListCreateApi.as_view(),
        name='car-wash-surcharge-list-create',
    ),
    path(
        r'car-washes/surcharges/<int:surcharge_id>/',
        CarWashSurchargeDeleteApi.as_view(),
        name='car-wash-surcharge-delete',
    ),
    path(
        r'car-washes/penalties/<int:penalty_id>/',
        CarWashPenaltyDeleteApi.as_view(),
        name='car-wash-penalty-delete',
    ),
    path(
        r'penalties/',
        PenaltyListCreateApi.as_view(),
        name='penalty-list-create',
    ),
    path(
        r'penalties/<int:penalty_id>/',
        CarTransporterPenaltyDeleteApi.as_view(),
        name='car-transporter-penalty-delete',
    ),
    path(
        r'surcharges/', SurchargeCreateApi.as_view(), name='surcharge-create'
    ),
    path(
        r'surcharges/<int:surcharge_id>/',
        CarTransporterSurchargeDeleteApi.as_view(),
        name='car-transporter-surcharge-delete',
    ),
    path(r'reports/', include(reports_urlpatterns)),
]
