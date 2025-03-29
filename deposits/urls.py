from django.urls import path

from deposits.views import DepositListApi


app_name = "deposits"
urlpatterns = [
    path(r'', DepositListApi.as_view(), name='list'),
]
