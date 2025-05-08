from django.urls import include, path

from economics.views import (
    CarTransporterPenaltyListCreateApi,
    CarWashesRevenueApi,
    StaffShiftsStatisticsReportApi,
    CarTransporterSurchargeListCreateApi,
    CarWashPenaltyListCreateApi,
    CarWashSurchargeListCreateApi,
    CarWashSurchargeDeleteApi,
    CarWashPenaltyDeleteApi,
    CarTransporterPenaltyDeleteApi,
    CarTransporterSurchargeDeleteApi,
)


reports_urlpatterns = [
    path(
        r"service-costs/",
        CarWashesRevenueApi.as_view(),
        name="service-costs",
    ),
    path(
        r"staff-shifts-statistics/",
        StaffShiftsStatisticsReportApi.as_view(),
        name="staff-shifts-statistics",
    ),
]

app_name = "economics"
urlpatterns = [
    path(
        r"car-washes/penalties/",
        CarWashPenaltyListCreateApi.as_view(),
        name="car-wash-penalty-list-create",
    ),
    path(
        r"car-washes/surcharges/",
        CarWashSurchargeListCreateApi.as_view(),
        name="car-wash-surcharge-list-create",
    ),
    path(
        r"car-washes/surcharges/<int:surcharge_id>/",
        CarWashSurchargeDeleteApi.as_view(),
        name="car-wash-surcharge-delete",
    ),
    path(
        r"car-washes/penalties/<int:penalty_id>/",
        CarWashPenaltyDeleteApi.as_view(),
        name="car-wash-penalty-delete",
    ),
    path(
        r"car-transporters/penalties/",
        CarTransporterPenaltyListCreateApi.as_view(),
        name="car-transporter-penalty-list-create",
    ),
    path(
        r"car-transporters/penalties/<int:penalty_id>/",
        CarTransporterPenaltyDeleteApi.as_view(),
        name="car-transporter-penalty-delete",
    ),
    path(
        r"car-transporters/surcharges/",
        CarTransporterSurchargeListCreateApi.as_view(),
        name="car-transporter-surcharge-list-create",
    ),
    path(
        r"car-transporters/surcharges/<int:surcharge_id>/",
        CarTransporterSurchargeDeleteApi.as_view(),
        name="car-transporter-surcharge-delete",
    ),
    path(r"reports/", include(reports_urlpatterns)),
]
