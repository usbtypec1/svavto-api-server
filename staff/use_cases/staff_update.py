from dataclasses import dataclass

from staff.selectors import ensure_staff_exists
from staff.services import update_staff


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffUpdateUseCase:
    staff_id: int
    is_banned: bool
    staff_type: int

    def execute(self) -> None:
        ensure_staff_exists(self.staff_id)
        update_staff(
            staff_id=self.staff_id,
            staff_type=self.staff_type,
            is_banned=self.is_banned,
        )
