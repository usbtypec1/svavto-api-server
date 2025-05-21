
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from deposits.views import DepositListApi, RoadAccidentDepositExceptionViewSet


router = SimpleRouter()
router.register(
    r'exceptions/road-accident',
    RoadAccidentDepositExceptionViewSet,
    basename='road-accident-deposit-exception',
)


app_name = "deposits"
urlpatterns = [
    path(r'', DepositListApi.as_view(), name='list'),
    path(r'', include(router.urls)),
]
