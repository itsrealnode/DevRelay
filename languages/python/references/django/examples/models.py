from django.db import models


class BaseAbstractModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        abstract = True


class Example(BaseAbstractModel):
    title = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self) -> str:
        return self.title


class ExampleMaterial(BaseAbstractModel):
    name = models.CharField(max_length=200)
    example = models.ForeignKey(
        Example,
        related_name="materials",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("pk",)

    def __str__(self) -> str:
        return self.name
