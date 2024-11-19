from django.urls import path

from car_washes.views import (
    CarWashAllServicesApi,
    CarWashListCreateApi,
    CarWashRetrieveUpdateDeleteApi,
    CarWashServicePriceUpsertApi,
    CarWashServicesApi,
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
        CarWashServicesApi.as_view(),
        name='services',
    ),
    path(
        r'<int:car_wash_id>/services/<uuid:service_id>/prices/',
        CarWashServicePriceUpsertApi.as_view(),
        name='service-price-upsert',
    ),
]
