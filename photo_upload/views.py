from uuid import uuid4

from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from photo_upload.exceptions import (
    PhotoNotProvidedError,
    PhotoNotUploadedError,
)
from photo_upload.services import upload_in_memory_file


class PhotoUploadApi(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request: Request):
        try:
            file = request.FILES['photo']
        except KeyError:
            raise PhotoNotProvidedError

        folder = request.data.get('folder')

        result = upload_in_memory_file(file, folder=folder)

        response_data = {'object_name': result.object_name, 'url': result.url}
        return Response(response_data, status.HTTP_201_CREATED)
