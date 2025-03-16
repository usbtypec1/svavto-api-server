import datetime
from collections.abc import Iterable
from uuid import UUID

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


__all__ = (
    "StaffHasNoActiveShiftError",
    "CarWashSameAsCurrentError",
    "ShiftByDateNotFoundError",
    "StaffHasActiveShiftError",
    "ShiftAlreadyFinishedError",
    "StaffHasNoAnyShiftError",
    "ShiftNotFoundError",
    "CarAlreadyWashedOnShiftError",
    "ShiftAlreadyExistsError",
    "AdditionalServiceCouldNotBeProvidedError",
    "StaffServicePriceNotFoundError",
    "CarToWashNotFoundError",
    "MonthNotAvailableError",
    "ShiftNotConfirmedError",
    "InvalidTimeToStartShiftError",
    "ShiftAlreadyConfirmedError",
)


class StaffHasNoActiveShiftError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("staff has no active shift")
    default_code = "staff_has_no_active_shift"


class CarWashSameAsCurrentError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("car wash is the same as the current one")
    default_code = "car_wash_same_as_current"


class ShiftByDateNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("shift for the specific date not found")
    default_code = "shift_for_specific_date_not_found"


class StaffHasActiveShiftError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("staff has active shift")
    default_code = "staff_has_active_shift"


class ShiftAlreadyFinishedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("shift is already finished")
    default_code = "shift_already_finished"

    def __init__(self, *, shift_date: datetime.date):
        super().__init__(self.default_detail)
        self.extra = {"shift_date": shift_date}


class StaffHasNoAnyShiftError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("staff has no any shift")
    default_code = "staff_has_no_any_shift"


class ShiftNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("shift not found")
    default_code = "shift_not_found"


class CarAlreadyWashedOnShiftError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("car was already washed on the shift")
    default_code = "car_already_washed_on_shift"


class ShiftAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("shift already exists")
    default_code = "shift_already_exists"

    def __init__(self, conflict_dates: Iterable[datetime.date]):
        """
        Args:
            conflict_dates: Dates of the existing shifts.
        """
        super().__init__(self.default_detail)
        self.extra = {"conflict_dates": conflict_dates}


class AdditionalServiceCouldNotBeProvidedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("additional service could not be provided")
    default_code = "additional_service_could_not_be_provided"

    def __init__(self, service_ids: Iterable[UUID]):
        """
        Args:
            service_ids: Service IDs that could not be provided.
        """
        super().__init__(self.default_detail)
        self.extra = {"service_ids": service_ids}


class StaffServicePriceNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("staff service price not found")
    default_code = "staff_service_price_not_found"


class CarToWashNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("car to wash not found")
    default_code = "car_to_wash_not_found"

    def __init__(self, car_to_wash_id: int):
        super().__init__(self.default_detail)
        self.extra = {"car_to_wash_id": car_to_wash_id}


class MonthNotAvailableError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "month_not_available"
    default_detail = _("month is not available")

    def __init__(self, *, year: int, month: int):
        super().__init__(self.default_detail)
        self.extra = {"year": year, "month": month}


class ShiftNotConfirmedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "shift_not_confirmed"
    default_detail = _("shift is not confirmed")


class InvalidTimeToStartShiftError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "invalid_time_to_start_shift"
    default_detail = _("invalid time to start the shift")


class ShiftAlreadyConfirmedError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "shift_already_confirmed"
    default_detail = _("shift is already confirmed")
