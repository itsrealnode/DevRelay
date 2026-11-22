from uuid import UUID

from pydantic import BaseModel, Field


class ExampleCreateRequest(BaseModel):
    title: str = Field(max_length=255)
    description: str


class ExampleResponse(BaseModel):
    id: UUID
    title: str
    description: str
