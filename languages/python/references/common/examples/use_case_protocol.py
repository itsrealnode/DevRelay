from typing import Protocol


class IUseCase[InputData, OutputData](Protocol):
    async def __call__(self, *, input_data: InputData) -> OutputData: ...
