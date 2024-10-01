from typing import Any

import drf_standardized_errors.formatter
from drf_standardized_errors.types import ErrorResponse


class ExceptionFormatter(drf_standardized_errors.formatter.ExceptionFormatter):

    def format_error_response(self, error_response: ErrorResponse) -> Any:
        extra: dict | None = getattr(self.exc, 'extra', None)

        error_response = super().format_error_response(error_response)
        for error in error_response['errors']:
            if extra is not None and error['code'] == self.exc.default_code:
                error['extra'] = extra

        return error_response
