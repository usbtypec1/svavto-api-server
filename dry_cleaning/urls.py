from django.urls import path, include

from dry_cleaning.views import (
    DryCleaningRequestApproveApi, DryCleaningRequestListCreateApi,
    DryCleaningRequestRejectApi, DryCleaningRequestRetrieveApi,
    DryCleaningAdminListApi,
)


requests_urlpatterns = [
    path(
        r'',
        DryCleaningRequestListCreateApi.as_view(),
        name='dry-cleaning-request-list-create',
    ),
    path(
        r'<int:dry_cleaning_request_id>/',
        DryCleaningRequestRetrieveApi.as_view(),
        name='dry-cleaning-request-retrieve',
    ),
    path(
        r'<int:dry_cleaning_request_id>/approve/',
        DryCleaningRequestApproveApi.as_view(),
        name='dry-cleaning-request-approve',
    ),
    path(
        r'<int:dry_cleaning_request_id>/reject/',
        DryCleaningRequestRejectApi.as_view(),
        name='dry-cleaning-request-reject',
    ),
    path(
        r'admins/',
        DryCleaningAdminListApi.as_view(),
        name='dry-cleaning-admin-list',
    )
]

urlpatterns = [
    path(r'requests/', include(requests_urlpatterns)),
]
