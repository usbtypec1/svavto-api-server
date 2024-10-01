from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException

__all__ = ('PerformerNotFoundError', 'PerformerAlreadyExistsError')


class PerformerNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'performer_not_found'
    default_detail = _('Performer was not found')


class PerformerAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'performer_already_exists'
    default_detail = _('Performer already exists')
