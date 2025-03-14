from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from dry_cleaning.models.dry_cleaning_admins import DryCleaningAdmin


class DryCleaningAdminListApi(APIView):

    def get(self, request: Request) -> Response:
        admins = DryCleaningAdmin.objects.values('id', 'name')
        return Response({'admins': admins})
