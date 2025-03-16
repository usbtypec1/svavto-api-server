from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class DryCleaningRequestNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "dry_cleaning_request_not_found"
    default_detail = _("Dry cleaning request not found")


class DryCleaningRequestInvalidStatusError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "dry_cleaning_request_invalid_status"
    default_detail = _("Dry cleaning request has invalid status")
