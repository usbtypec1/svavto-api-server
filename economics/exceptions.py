from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException

__all__ = ('InvalidPenaltyConsequenceError',)


class InvalidPenaltyConsequenceError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'invalid_penalty_consequence'
    default_detail = _('invalid penalty consequence')
