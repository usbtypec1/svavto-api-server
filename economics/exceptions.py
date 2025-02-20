from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


__all__ = (
    'InvalidPenaltyConsequenceError',
    'CarTransporterPenaltyNotFoundError',
    'CarTransporterSurchargeNotFoundError',
)


class InvalidPenaltyConsequenceError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'invalid_penalty_consequence'
    default_detail = _('invalid penalty consequence')

    def __init__(
            self,
            staff_id: int,
            penalty_reason: str,
            penalties_count: int,
    ):
        """
        Args:
            staff_id: staff member's ID.
            penalty_reason: reason for penalty.
            penalties_count: penalties count that staff member already had.
        """
        self.extra = {
            'staff_id': staff_id,
            'penalty_reason': penalty_reason,
            'penalties_count': penalties_count,
        }


class CarTransporterPenaltyNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'car_transfer_penalty_not_found'
    default_detail = _('Car transfer penalty not found')


class CarTransporterSurchargeNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'car_transfer_surcharge_not_found'
    default_detail = _('Car transfer surcharge not found')
