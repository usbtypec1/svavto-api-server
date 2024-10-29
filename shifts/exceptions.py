from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException

__all__ = ('StaffHasNoActiveShiftError',)


class StaffHasNoActiveShiftError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Staff has no active shift')
    default_code = 'staff_has_no_active_shift'
