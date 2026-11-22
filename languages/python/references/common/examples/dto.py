from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True, slots=True)
class ExampleCreateInputDTO:
    title: str
    description: str


@dataclass(kw_only=True, frozen=True, slots=True)
class ExampleDTO(ExampleCreateInputDTO):
    id: UUID
