from django.urls import path

from economics.views import (
    SurchargeCreateApi,
    PenaltyListCreateApi,
    ServiceCostsApi,
)

urlpatterns = [
    path(
        r'penalties/',
        PenaltyListCreateApi.as_view(),
        name='penalty-list-create',
    ),
    path(r'surcharges/', SurchargeCreateApi.as_view(), name='surcharge-create'),
    path(
        r'reports/service-costs/',
        ServiceCostsApi.as_view(),
        name='service-costs',
    ),
]
