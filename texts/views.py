from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from texts.exceptions import TextNotFoundError
from texts.models import Text


class TextRetrieveApi(APIView):

    def get(self, request: Request) -> Response:
        try:
            text = Text.objects.get(key=request.query_params.get('key'))
        except Text.DoesNotExist:
            raise TextNotFoundError
        return Response({'key': text.key, 'value': text.value})
