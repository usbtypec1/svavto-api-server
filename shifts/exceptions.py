from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException

__all__ = (
    'StaffHasNoActiveShiftError',
    'CarWashSameAsCurrentError',
    'ShiftByDateNotFoundError',
    'ShiftNotConfirmedError',
    'StaffHasActiveShiftError',
    'ShiftAlreadyFinishedError',
    'ShiftAlreadyConfirmedError',
    'StaffHasNoAnyShiftError',
    'ShiftNotFoundError',
    'CarAlreadyWashedOnShiftError',
)


class StaffHasNoActiveShiftError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Staff has no active shift')
    default_code = 'staff_has_no_active_shift'


class CarWashSameAsCurrentError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('Car wash is the same as the current one')
    default_code = 'car_wash_same_as_current'


class ShiftByDateNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Shift for the specific date not found')
    default_code = 'shift_for_specific_date_not_found'


class ShiftNotConfirmedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Shift is not confirmed')
    default_code = 'shift_not_confirmed'


class StaffHasActiveShiftError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Staff has active shift')
    default_code = 'staff_has_active_shift'


class ShiftAlreadyFinishedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Shift is already finished')
    default_code = 'shift_already_finished'


class ShiftAlreadyConfirmedError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('Shift is already confirmed')
    default_code = 'shift_already_confirmed'


class StaffHasNoAnyShiftError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Staff has no any shift')
    default_code = 'staff_has_no_any_shift'


class ShiftNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Shift not found')
    default_code = 'shift_not_found'


class CarAlreadyWashedOnShiftError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('Car was already washed on the shift')
    default_code = 'car_already_washed_on_shift'
