from django.urls import path

from car_washes.views import (
    CarWashAllServicesApi,
    CarWashListCreateApi,
    CarWashRetrieveUpdateDeleteApi,
    SpecificCarWashServiceUpdateDeleteApi,
    SpecificCarWashServiceListApi,
)

app_name = 'car_washes'
urlpatterns = [
    path(r'', CarWashListCreateApi.as_view(), name='wash-list-create'),
    path(
        r'<int:car_wash_id>/',
        CarWashRetrieveUpdateDeleteApi.as_view(),
        name='detail-update-delete',
    ),
    path(
        r'services/',
        CarWashAllServicesApi.as_view(),
        name='all-services',
    ),
    path(
        r'<int:car_wash_id>/services/',
        SpecificCarWashServiceListApi.as_view(),
        name='specific-service-list',
    ),
    path(
        r'<int:car_wash_id>/services/<uuid:service_id>/',
        SpecificCarWashServiceUpdateDeleteApi.as_view(),
        name='specific-service-update-delete',
    ),
]
