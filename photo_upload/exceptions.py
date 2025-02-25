from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class PhotoNotProvidedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'photo_not_provided'
    default_detail = _('Photo not provided')


class PhotoNotUploadedError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = 'photo_not_uploaded'
    default_detail = _('Photo not uploaded')
