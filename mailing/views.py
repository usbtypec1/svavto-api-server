from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from mailing.serializers import MailingSerializer
from mailing.tasks import (
    start_mailing_to_staff_with_latest_activity,
    start_mailing_all_staff,
    start_mailing_for_specific_staff,
)

__all__ = (
    'MailingToAllStaffApi',
    'MailingToSpecificStaffApi',
    'MailingToStaffWithLatestActivityApi',
)


class MailingToAllStaffApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = MailingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        text = serialized_data['text']
        reply_markup = serialized_data['reply_markup']

        start_mailing_all_staff.delay(text=text, buttons_rows=reply_markup)
        return Response(status=status.HTTP_202_ACCEPTED)


class MailingToSpecificStaffApi(APIView):
    class InputSerializer(MailingSerializer):
        chat_ids = serializers.ListField(child=serializers.IntegerField())

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        text = serialized_data['text']
        chat_ids = serialized_data['chat_ids']
        reply_markup = serialized_data['reply_markup']

        start_mailing_for_specific_staff.delay(
            text=text,
            chat_ids=chat_ids,
            buttons_rows=reply_markup,
        )
        return Response(status=status.HTTP_202_ACCEPTED)


class MailingToStaffWithLatestActivityApi(APIView):
    class InputSerializer(MailingSerializer):
        last_days = serializers.IntegerField(min_value=1, max_value=90)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        text = serialized_data['text']
        last_days = serialized_data['last_days']

        start_mailing_to_staff_with_latest_activity.delay(
            text=text,
            last_days=last_days,
        )
        return Response(status=status.HTTP_202_ACCEPTED)
