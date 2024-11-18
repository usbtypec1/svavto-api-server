from rest_framework.generics import ListAPIView

from staff.models import AdminStaff
from staff.serializers import AdminStaffListSerializer

__all__ = ('AdminStaffListApi',)


class AdminStaffListApi(ListAPIView):
    serializer_class = AdminStaffListSerializer
    queryset = AdminStaff.objects.all()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {'admin_staff': response.data}
        return response
