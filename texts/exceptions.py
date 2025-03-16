from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework import status


class TextNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("Text not found")
    default_code = "text_not_found"
