from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from deposits.models import FineDepositException


class FineDepositExceptionResource(ModelResource):

    class Meta:
        model = FineDepositException


@admin.register(FineDepositException)
class FineDepositExceptionAdmin(ImportExportModelAdmin):
    resource_class = FineDepositExceptionResource
    autocomplete_fields = ('staff',)
