from collections.abc import Sequence

from django.utils import timezone

from .models import Example, ExampleMaterial


class ExampleMaterialsUnavailable(Exception):
    """Хотя бы один из запрошенных материалов отсутствует или уже занят."""


class ExampleMaterialService:
    @staticmethod
    def attach(example: Example, material_ids: Sequence[int]) -> None:
        """Привязать свободные материалы внутри транзакции создания записи."""
        requested_ids = set(material_ids)
        if not requested_ids:
            return
        attached = ExampleMaterial.objects.filter(
            pk__in=requested_ids, example__isnull=True
        ).update(example=example, updated_at=timezone.now())
        if attached != len(requested_ids):
            raise ExampleMaterialsUnavailable
