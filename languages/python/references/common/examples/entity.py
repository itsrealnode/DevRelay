from dataclasses import dataclass
from uuid import UUID


@dataclass
class Example:
    id: UUID
    title: str
    description: str
