from rest_framework import serializers

from .models import Example, ExampleMaterial


class ExampleInputSerializer(serializers.ModelSerializer):
    material_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), write_only=True, required=False
    )

    class Meta:
        model = Example
        fields = ("title", "date", "material_ids")


class ExampleMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleMaterial
        fields = ("id", "name")


class ExampleDetailSerializer(serializers.ModelSerializer):
    materials = ExampleMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Example
        fields = ("id", "title", "date", "materials")
