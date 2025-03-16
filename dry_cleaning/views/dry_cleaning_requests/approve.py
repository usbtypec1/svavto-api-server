from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers.dry_cleaning_requests import (
    DryCleaningRequestApproveInputSerializer,
)
from shifts.services import DryCleaningRequestApproveInteractor


class DryCleaningRequestApproveApi(APIView):
    def post(self, request: Request, dry_cleaning_request_id: int) -> Response:
        serializer = DryCleaningRequestApproveInputSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        DryCleaningRequestApproveInteractor(
            dry_cleaning_request_id=dry_cleaning_request_id,
            response_comment=serializer.validated_data["response_comment"],
            services=serializer.validated_data["services"],
        ).execute()
        return Response()
