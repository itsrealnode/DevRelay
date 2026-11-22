from rest_framework import mixins, serializers, status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from .dto import ExampleDTO
from .models import Example, ExampleMaterial
from .serializers import ExampleDetailSerializer, ExampleInputSerializer, ExampleMaterialSerializer
from .services import ExampleMaterialsUnavailable
from .use_case import ExampleUseCase


class ExampleViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Example.objects.prefetch_related("materials")
    serializer_class = ExampleDetailSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return ExampleInputSerializer
        return ExampleDetailSerializer

    def create(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        data = ExampleDTO(
            title=values["title"],
            date=values["date"],
            material_ids=tuple(values.get("material_ids", ())),
        )
        try:
            example = ExampleUseCase(data=data).execute()
        except ExampleMaterialsUnavailable as error:
            raise serializers.ValidationError(
                {"material_ids": ["Один или несколько материалов недоступны."]}
            ) from error
        result = ExampleDetailSerializer(example, context=self.get_serializer_context())
        return Response(result.data, status=status.HTTP_201_CREATED)


class BaseModelViewSet(viewsets.ModelViewSet):
    """Полный CRUD для сотрудников через стандартные действия DRF."""

    permission_classes = (IsAdminUser,)


class ExampleMaterialViewSet(BaseModelViewSet):
    queryset = ExampleMaterial.objects.all()
    serializer_class = ExampleMaterialSerializer
