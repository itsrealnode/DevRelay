# Примеры FastAPI

В примере `ExampleUseCase` открывает UoW, вызывает репозиторий и собирает `ExampleDTO` из доменной сущности. При успешном выходе UoW подтверждает транзакцию. Затем запись можно прочитать по полученному UUID в отдельном запросе.

## Как выбрать пример

Сначала найди аналог конкретной части в целевом проекте. Проверь соседний модуль, импорты и точку сборки приложения. Используй его соглашения об именовании, вызове и владении транзакцией. Если аналога нет, выбери нужный файл из таблицы и замени `Example` предметным именем из задачи.

| Часть | Файлы примера | Что посмотреть |
|---|---|---|
| Прикладной сценарий | [use_case.py](../../common/examples/use_case.py) · [use_case_protocol.py](../../common/examples/use_case_protocol.py) | Вызов с именованными аргументами. Создание и чтение используют готовые методы репозитория. |
| Сущность и DTO | [entity.py](../../common/examples/entity.py) · [dto.py](../../common/examples/dto.py) | UUID, название и описание. DTO со свойствами `kw_only=True, frozen=True, slots=True`. |
| Контракт хранилища | [repository_protocol.py](../../common/examples/repository_protocol.py) | Создание возвращает сущность. Чтение по UUID допускает `None`. |
| ORM и репозиторий | [models.py](models.py) · [sqlalchemy_repository.py](sqlalchemy_repository.py) | Запись через `INSERT ... RETURNING`, поиск через `select` и `scalar_one_or_none()`, преобразование ORM в доменную сущность. |
| Граница транзакции | [uow_protocol.py](../../common/examples/uow_protocol.py) · [uow.py](uow.py) | UoW открывает транзакцию, подтверждает её при успехе и откатывает при исключении. |

## HTTP и Dishka

Демо показывает предметные маршруты, Pydantic-схемы и интеграцию Dishka.

| Задача | Пример | Что посмотреть |
|---|---|---|
| Принять запрос и вернуть результат | [router.py](router.py) · [schemas.py](schemas.py) | POST собирает входной DTO из тела запроса. GET принимает UUID и превращает отсутствие сущности в HTTP 404. Публичные поля ответа задаёт `ExampleResponse`. |
| Зарегистрировать зависимости | [dishka_provider.py](dishka_provider.py) | Движок общий для приложения. UoW и репозиторий получают одну сессию на запрос. Транзакцию открывает UoW. |
| Собрать приложение | [demo.py](demo.py) | Фабрика подключает роутер и контейнер. При запуске создаёт пустую таблицу в SQLite в памяти, при остановке освобождает ресурсы. |

Если в целевом проекте уже есть роутер, схемы и Dishka-провайдер сессий, а задача требует зарегистрировать use case, достаточно взять нужные привязки из провайдера. Если проект собирает зависимости вручную или через `Depends`, подключи use case существующим способом.

## Как проверить

Запусти приложение из каталога `languages/python`. Версии в [requirements.txt](requirements.txt) подобраны для автономного примера.

```sh
uv run --no-project --python 3.12 --with-requirements references/fastapi/examples/requirements.txt \
  python -m uvicorn references.fastapi.examples.demo:create_app --factory
```

В другом терминале создай запись. Ответ содержит статус `201`, сгенерированный `id` и присланные поля.

```sh
curl -i http://127.0.0.1:8000/examples \
  -H 'Content-Type: application/json' \
  -d '{"title":"Example","description":"First entry"}'
```

Подставь полученный UUID вместо `<id>` в `GET /examples/<id>`. Ответ `200` содержит ту же запись. Для отсутствующего UUID вернётся `404`, для `GET /examples/abc` вернётся `422`. При новом запуске SQLite снова пуста.
