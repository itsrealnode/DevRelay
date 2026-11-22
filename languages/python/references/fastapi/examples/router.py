from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, status

from references.common.examples.dto import ExampleCreateInputDTO, ExampleDTO
from references.common.examples.use_case import ExampleUseCase, GetExampleUseCase

from .schemas import ExampleCreateRequest, ExampleResponse

router = APIRouter(prefix="/examples", tags=["examples"], route_class=DishkaRoute)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ExampleResponse)
async def create_example(body: ExampleCreateRequest, use_case: FromDishka[ExampleUseCase]) -> ExampleDTO:
    return await use_case(input_data=ExampleCreateInputDTO(title=body.title, description=body.description))


@router.get("/{example_id}", response_model=ExampleResponse)
async def get_example(example_id: UUID, use_case: FromDishka[GetExampleUseCase]) -> ExampleDTO:
    example = await use_case(input_data=example_id)
    if example is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Example not found")
    return example
