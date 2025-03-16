from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import DryCleaningRequestSerializer
from shifts.services import DryCleaningRequestRetrieveByIdInteractor


class DryCleaningRequestRetrieveApi(APIView):
    def get(self, request: Request, dry_cleaning_request_id: int) -> Response:
        dry_cleaning_request = DryCleaningRequestRetrieveByIdInteractor(
            dry_cleaning_request_id=dry_cleaning_request_id,
        ).execute()
        serializer = DryCleaningRequestSerializer(dry_cleaning_request)
        return Response(serializer.data)
