from django.contrib import admin

from .models import Example, ExampleMaterial


class ExampleMaterialInline(admin.TabularInline):
    model = ExampleMaterial
    extra = 0


@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    list_display = ("title", "date")
    list_filter = ("date",)
    search_fields = ("title",)
    inlines = (ExampleMaterialInline,)
