# Примеры Django и DRF

Используй подходящий пример, когда в целевом проекте нет аналога для конкретной части задачи. Сначала проверь соседние приложения, их базовые классы и правила доступа. Если нужен только сериализатор, достаточно открыть [serializers.py](serializers.py).

Клиент присылает название, дату и список заранее загруженных материалов. ViewSet валидирует вход, собирает `ExampleDTO` и вызывает `ExampleUseCase(data=data).execute()`. Сценарий в одной транзакции создаёт запись и привязывает материалы. ViewSet возвращает созданную модель через отдельный сериализатор ответа.

Второй пример в [viewsets.py](viewsets.py) показывает полный CRUD материалов. `BaseModelViewSet` наследует все стандартные действия от DRF `ModelViewSet` и задаёт общий доступ для сотрудников. В `ExampleMaterialViewSet` достаточно указать queryset и сериализатор.

| Маршрут | Методы | Действия |
|---|---|---|
| `/materials/` | GET, POST | `list`, `create` |
| `/materials/<id>/` | GET, PUT, PATCH, DELETE | `retrieve`, `update`, `partial_update`, `destroy` |

| Компонент | Пример |
|---|---|
| ViewSet и маршрут | [viewsets.py](viewsets.py), [urls.py](urls.py) |
| Вход и ответ API | [serializers.py](serializers.py) |
| Входной DTO с именованными полями | [dto.py](dto.py) |
| Сценарий и транзакция | [use_case.py](use_case.py) |
| Привязка существующих материалов через ORM | [services.py](services.py) |
| Модели и обратная связь | [models.py](models.py) |
| Admin и редактирование связанных строк | [admin.py](admin.py) |

**Доступ.** Демо использует `is_staff`. При переносе используй права целевого приложения, включая проверки объекта и полей, если этого требует его контракт.

**Как проверить.** Добавь каталог `languages/python` в путь импорта Python для тестового Django-проекта с DRF. Добавь `references.django.examples` в `INSTALLED_APPS`, подключи `references.django.examples.urls` и создай таблицы в тестовой БД. Создай свободный `ExampleMaterial` и подставь его ID в запрос:

```http
POST /examples/
Content-Type: application/json

{"title":"Example","date":"2026-11-22","material_ids":[1]}
```

Ответ `201` содержит `id`, `title`, `date` и массив `materials` с полями `id` и `name`. Последующий `GET /examples/<id>/` возвращает те же данные. Если запрос на создание содержит одновременно свободный и занятый материал, ожидай ошибку `400` по полю `material_ids`. Проверь в БД обе части отката: новая запись отсутствует, свободный материал по-прежнему доступен.
