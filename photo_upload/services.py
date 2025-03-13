import io
from dataclasses import dataclass
from typing import BinaryIO
from uuid import uuid4

import httpx
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from minio import Minio

from photo_upload.exceptions import PhotoNotUploadedError


def get_s3_client() -> Minio:
    return Minio(
        endpoint=settings.S3_ENDPOINT,
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class UploadedFile:
    object_name: str
    url: str


def upload_binary(
        file_io: BinaryIO,
        length: int,
        content_type: str,
        object_name: str,
) -> UploadedFile:
    file_io.seek(0)
    try:
        result = get_s3_client().put_object(
            bucket_name=settings.S3_BUCKET_NAME,
            object_name=object_name,
            data=file_io,
            length=length,
            content_type=content_type,
        )
    except Exception as error:
        raise PhotoNotUploadedError from error
    return UploadedFile(
        object_name=result.object_name,
        url=get_public_url(result.object_name),
    )


def upload_in_memory_file(
        file: BinaryIO | InMemoryUploadedFile,
        folder: str | None = None,
) -> UploadedFile:
    object_name = build_object_name(file.name, folder)
    return upload_binary(
        file_io=file,
        length=file.size,
        content_type=file.content_type,
        object_name=object_name,
    )


def build_object_name(name: str, folder: str | None = None) -> str:
    ext = name.split(".")[-1] if "." in name else ""
    object_name = f"{uuid4().hex}.{ext}" if ext else uuid4().hex
    if folder:
        object_name = f"{folder}/{object_name}"
    return object_name


def upload_via_url(
        url: str,
        folder: str | None = None,
) -> UploadedFile:
    response = httpx.get(url)
    response.raise_for_status()
    object_name = build_object_name(url, folder)
    with io.BytesIO(response.content) as file_io:
        return upload_binary(
            file_io=file_io,
            length=len(response.content),
            content_type=response.headers.get(
                "Content-Type", "application/octet-stream"
            ),
            object_name=object_name,
        )


def get_public_url(object_name: str) -> str:
    return (
        f'https://{settings.S3_ENDPOINT}/{settings.S3_BUCKET_NAME}/'
        f'{object_name}'
    )
