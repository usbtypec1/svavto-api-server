from typing import Final

from django.core.management import BaseCommand

from economics.models import StaffServicePrice

SERVICE_TYPE_TO_PRICE: Final[dict[StaffServicePrice.ServiceType, int]] = {
    StaffServicePrice.ServiceType.COMFORT_CLASS_CAR_TRANSFER: 170,
    StaffServicePrice.ServiceType.BUSINESS_CLASS_CAR_TRANSFER: 180,
    StaffServicePrice.ServiceType.VAN_TRANSFER: 190,
    StaffServicePrice.ServiceType.CAR_TRANSPORTER_EXTRA_SHIFT: 190,
    StaffServicePrice.ServiceType.URGENT_CAR_WASH: 250,
    StaffServicePrice.ServiceType.ITEM_DRY_CLEAN: 50,
    StaffServicePrice.ServiceType.UNDER_PLAN_PLANNED_CAR_TRANSFER: 100,
}


class Command(BaseCommand):
    help = "Initialize staff service prices"

    def handle(self, *args, **options):
        for service_type in StaffServicePrice.ServiceType:
            if service_type not in SERVICE_TYPE_TO_PRICE:
                self.stderr.write(
                    self.style.WARNING(
                        "Service type %s is not in SERVICE_TYPE_TO_PRICE",
                    )
                )
            StaffServicePrice.objects.update_or_create(
                service=service_type,
                defaults={
                    "price": SERVICE_TYPE_TO_PRICE[service_type],
                },
            )
        self.stdout.write(
            self.style.SUCCESS(
                "Staff service prices have been initialized",
            )
        )
