from typing import Self


class SingleRowModelMixin:

    @classmethod
    def get(cls) -> Self:
        obj = cls.objects.first()
        if obj is None:
            raise ValueError("Single-row model object not found")
        return obj
