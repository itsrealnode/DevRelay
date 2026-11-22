from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, kw_only=True, slots=True)
class ExampleDTO:
    title: str
    date: date
    material_ids: tuple[int, ...] = ()
