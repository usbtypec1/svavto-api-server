import gspread
from django.conf import settings

__all__ = ('create_google_sheets_client',)


def create_google_sheets_client() -> gspread.Client:
    return gspread.service_account_from_dict(
        settings.GOOGLE_SHEETS_SERVICE_ACCOUNT_CREDENTIALS,
    )
