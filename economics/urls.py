from django.urls import path

from economics.views import (
    SurchargeCreateApi,
    PenaltyListCreateApi,
)

urlpatterns = [
    path(
        r'penalties/',
        PenaltyListCreateApi.as_view(),
        name='penalty-list-create',
    ),
    path(r'surcharges/', SurchargeCreateApi.as_view(), name='surcharge-create'),
]
