from django.urls import path

from car_washes.views import (
    CarWashAllServicesApi,
    CarWashListCreateApi,
    CarWashRetrieveUpdateDeleteApi,
    SpecificCarWashServiceUpdateDeleteApi,
    CarWashServicePriceListApi,
)

app_name = "car-washes"
urlpatterns = [
    path(r"", CarWashListCreateApi.as_view(), name="wash-list-create"),
    path(
        r"<int:car_wash_id>/",
        CarWashRetrieveUpdateDeleteApi.as_view(),
        name="detail-update-delete",
    ),
    path(
        r"services/",
        CarWashAllServicesApi.as_view(),
        name="all-services",
    ),
    path(
        r"<int:car_wash_id>/services/<uuid:service_id>/",
        SpecificCarWashServiceUpdateDeleteApi.as_view(),
        name="specific-service-update-delete",
    ),
    path(
        r"<int:car_wash_id>/services/prices/",
        CarWashServicePriceListApi.as_view(),
        name="service-prices",
    ),
]
