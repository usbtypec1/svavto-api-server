from django.urls import path

from bonuses.views import BonusesExcludedStaffApi


app_name = 'bonuses'
urlpatterns = [
    path(
        r'excluded-staff/',
        BonusesExcludedStaffApi.as_view(),
        name='excluded-staff-list-update',
    ),
]
