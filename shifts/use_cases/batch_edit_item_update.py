from collections.abc import Iterable
from dataclasses import dataclass

from shifts.services.batch_edit import BatchEditService, Item


@dataclass(frozen=True, slots=True, kw_only=True)
class BatchEditItemUpdateUseCase:
    items: Iterable[Item]

    def execute(self) -> None:
        service = BatchEditService(items=self.items)
        service.delete_cars()
        service.update_cars()
        service.create_cars()
