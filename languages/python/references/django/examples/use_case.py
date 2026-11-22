from django.db import transaction

from .dto import ExampleDTO
from .models import Example
from .services import ExampleMaterialService


class ExampleUseCase:
    def __init__(self, data: ExampleDTO) -> None:
        self._data = data

    def execute(self) -> Example:
        with transaction.atomic():
            example = Example.objects.create(title=self._data.title, date=self._data.date)
            ExampleMaterialService.attach(example, self._data.material_ids)
        return example
