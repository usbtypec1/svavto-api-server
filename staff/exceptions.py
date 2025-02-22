from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException

__all__ = (
    'StaffNotFoundError',
    'StaffAlreadyExistsError',
    'StaffRegisterRequestAlreadyExistsError',
    'StaffRegisterRequestNotFoundError',
)


class StaffNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'staff_not_found'
    default_detail = _('staff was not found')


class StaffAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'staff_already_exists'
    default_detail = _('staff already exists')


class StaffRegisterRequestAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'staff_register_request_already_exists'
    default_detail = _('staff register request already exists')


class StaffRegisterRequestNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'staff_register_request_not_found'
    default_detail = _('staff register request was not found')
