from uuid import uuid4

import cloudinary.uploader
import cloudinary.exceptions
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from photo_upload.exceptions import (
    PhotoNotProvidedError,
    PhotoNotUploadedError,
)


class PhotoUploadApi(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request: Request):
        try:
            file = request.FILES['photo']
        except KeyError:
            raise PhotoNotProvidedError

        try:
            upload_result = cloudinary.uploader.upload(
                file=file,
                folder='svavto',
                public_id=uuid4().hex,
            )
        except cloudinary.exceptions.Error:
            raise PhotoNotUploadedError

        response_data = {
            'id': upload_result['public_id'],
            'url': upload_result['secure_url'],
        }
        return Response(response_data, status.HTTP_201_CREATED)
