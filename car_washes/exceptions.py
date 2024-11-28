from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException

__all__ = (
    'CarWashAlreadyExistsError',
    'CarWashNotFoundError',
    'CarWashServiceNotFoundError',
)


class CarWashAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'car_wash_already_exists'
    default_detail = _('car wash with this name already exists')


class CarWashNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'car_wash_not_found'
    default_detail = _('car wash was not found')


class CarWashServiceNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'car_wash_service_not_found'
    default_detail = _('car wash service was not found')
