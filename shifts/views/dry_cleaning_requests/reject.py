from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers.dry_cleaning_requests import (
    DryCleaningRequestRejectInputSerializer,
)
from shifts.services import DryCleaningRequestRejectInteractor


class DryCleaningRequestRejectApi(APIView):

    def post(self, request: Request, dry_cleaning_request_id: int) -> Response:
        serializer = DryCleaningRequestRejectInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        DryCleaningRequestRejectInteractor(
            dry_cleaning_request_id=dry_cleaning_request_id,
            response_comment=serializer.validated_data['response_comment'],
        ).execute()
        return Response()
