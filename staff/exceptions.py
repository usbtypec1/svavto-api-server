from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException

__all__ = (
    'StaffNotFoundError',
    'StaffAlreadyExistsError',
    'RegistrationAwaitingStaffAlreadyExistsError',
    'RegistrationAwaitingStaffNotFoundError',
)


class StaffNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'staff_not_found'
    default_detail = _('staff was not found')


class StaffAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'staff_already_exists'
    default_detail = _('staff already exists')


class RegistrationAwaitingStaffAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'staff_already_awaiting_registration'
    default_detail = _('staff already awaiting registration')


class RegistrationAwaitingStaffNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'registration_awaiting_staff_not_found'
    default_detail = _('registration awaiting staff was not found')
