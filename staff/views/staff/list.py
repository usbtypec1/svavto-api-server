from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.selectors import get_all_staff
from staff.serializers import (
    StaffListInputSerializer,
    StaffListOutputSerializer,
)

__all__ = ("StaffListApi",)


class StaffListApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = StaffListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        order_by: str = serialized_data["order_by"]
        include_banned: bool = serialized_data["include_banned"]
        limit: int = serialized_data["limit"]
        offset: int = serialized_data["offset"]

        staff_list_page = get_all_staff(
            order_by=order_by,
            include_banned=include_banned,
            limit=limit,
            offset=offset,
        )
        serializer = StaffListOutputSerializer(staff_list_page)
        return Response(serializer.data, status=status.HTTP_200_OK)
