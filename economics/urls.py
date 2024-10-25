from django.urls import path

from economics.views import PenaltyCreateApi, SurchargeCreateApi

urlpatterns = [
    path(r'penalties/', PenaltyCreateApi.as_view(), name='penalty-create'),
    path(r'surcharges/', SurchargeCreateApi.as_view(), name='surcharge-create'),
]
