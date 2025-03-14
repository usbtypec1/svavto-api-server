from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from dry_cleaning.models import (
    DryCleaningRequest, DryCleaningRequestPhoto, DryCleaningRequestService,
)


class DryCleaningRequestPhotoInline(admin.TabularInline):
    model = DryCleaningRequestPhoto
    extra = 0


class DryCleaningRequestServiceInline(admin.TabularInline):
    model = DryCleaningRequestService
    extra = 0


class DryCleaningRequestServiceResource(ModelResource):
    class Meta:
        model = DryCleaningRequestService


class DryCleaningRequestResource(ModelResource):
    class Meta:
        model = DryCleaningRequest


class DryCleaningRequestPhotoResource(ModelResource):
    class Meta:
        model = DryCleaningRequestPhoto


@admin.register(DryCleaningRequest)
class DryCleaningRequestAdmin(ImportExportModelAdmin):
    inlines = (DryCleaningRequestPhotoInline, DryCleaningRequestServiceInline)
    resource_class = DryCleaningRequestResource


@admin.register(DryCleaningRequestPhoto)
class DryCleaningRequestPhotoAdmin(ImportExportModelAdmin):
    resources_class = DryCleaningRequestPhotoResource


@admin.register(DryCleaningRequestService)
class DryCleaningRequestServiceAdmin(ImportExportModelAdmin):
    resource_class = DryCleaningRequestServiceResource
