from django.urls import path

from car_washes.views.list_create import CarWashListCreateApi

urlpatterns = [
    path(r'', CarWashListCreateApi.as_view(), name='car-wash-list-create'),
    path(
        r'<int:car_wash_id>/',
        CarWashListCreateApi.as_view(), name='car-wash-detail-update-delete'),
]