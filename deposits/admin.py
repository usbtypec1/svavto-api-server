from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from deposits.models import FineDepositException, RoadAccidentDepositException


class FineDepositExceptionResource(ModelResource):

    class Meta:
        model = FineDepositException


@admin.register(FineDepositException)
class FineDepositExceptionAdmin(ImportExportModelAdmin):
    resource_class = FineDepositExceptionResource
    autocomplete_fields = ('staff',)


class RoadAccidentDepositExceptionResource(ModelResource):

    class Meta:
        model = RoadAccidentDepositException


@admin.register(RoadAccidentDepositException)
class RoadAccidentDepositExceptionAdmin(ImportExportModelAdmin):
    resource_class = RoadAccidentDepositExceptionResource
    autocomplete_fields = ('staff',)
