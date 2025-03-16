from rest_framework import serializers

__all__ = ("StaffReportPeriodsOutputSerializer", "ReportPeriodSerializer")


class ReportPeriodSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()


class StaffReportPeriodsOutputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    periods = ReportPeriodSerializer(many=True)
