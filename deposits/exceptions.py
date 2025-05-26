from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework import status


class RoadAccidentDepositExceptionNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "road_accident_deposit_exception_not_found"
    default_detail = _("Road accident deposit exception not found.")


class FineDepositExceptionNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "fine_deposit_exception_not_found"
    default_detail = _("Fine deposit exception not found.")
