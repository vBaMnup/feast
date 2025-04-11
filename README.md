[![Run Tests](https://github.com/vBaMnup/feast/actions/workflows/tests.yml/badge.svg)](https://github.com/vBaMnup/feast/actions/workflows/tests.yml)

# Feast API

**Feast API** — это API-сервис для бронирования столиков, разработанный с использованием FastAPI, SQLAlchemy и PostgreSQL. Проект поддерживает функциональность создания, получения и удаления бронирований и столиков, а также включает автоматизированное тестирование, миграции Alembic и конфигурацию через Docker.


## Особенности

- **CRUD для столиков и бронирований:** Реализованы эндпоинты для создания, чтения и удаления данных.
- **Проверка конфликтов бронирований:** Сервис не позволяет создать бронь, если столик уже занят в заданное время.
- **Миграции Alembic:** Управление схемой базы данных посредством миграций.
- **Контейнеризация с Docker:** Проект полностью контейнеризирован для удобного развертывания в продакшене.
- **Логирование:** Настроенное логирование с использованием `logging.ini` для консольного и файлового вывода.
- **Настройки через Pydantic:** Конфигурация проекта с использованием Pydantic v2.

## Требования

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.12](https://www.python.org/downloads/)

## Установка

1. **Клонируйте репозиторий:**

```bash
git clone git@github.com:vBaMnup/feast.git
cd feast
```

2. **Настройте переменные окружения:**

Скопируйте и переименуйте `.env.example` в `.docker/.env` и заполните его данными.

```bash
cp .env.example .docker/.env
```

Скопируйте и переименуйте `.db.env.example` в `.docker/.db.env` и заполните его данными.

```bash
cp .db.env.example .docker/.db.env
```

3. **Установка зависимостей**

Для локальной разработки используйте виртуальное окружение и установку зависимостей из requirements:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements/dev.txt
```

## Запуск проекта
С использованием Docker

```bash
docker compose -f .docker/docker-compose.yml --env-file .docker/.db.env up -d --build
```

## Проверка работы API:

API запустится на порту 8000. Перейдите по адресу http://localhost:8000/health – вы должны увидеть ответ:

```json
{
  "status": "ok"
}
```
## Локальный запуск

Если вы запускаете приложение локально (без Docker), убедитесь, что настроены переменные окружения (например, в файле .env) и выполните команду:

```bash
python src/main.py
```

## Миграции базы данных
Проект использует Alembic для управления миграциями.

Создание новой миграции (автогенерация):

```bash
alembic revision --autogenerate -m "Initial migration"
```
Применение миграций:

```bash
alembic upgrade head
```
## Тестирование
Тесты написаны с использованием pytest. Чтобы запустить тесты, выполните:

```bash
pytest
```

Покрытие тестами:

```text
Name                            Stmts   Miss  Cover
---------------------------------------------------
src/__init__.py                     0      0   100%
src/config.py                      11      0   100%
src/database.py                    12      0   100%
src/logging_config.py              13      4    69%
src/main.py                        33      2    94%
src/reservation/__init__.py         0      0   100%
src/reservation/exceptions.py      21      0   100%
src/reservation/models.py          15      0   100%
src/reservation/router.py          19      0   100%
src/reservation/schemas.py         12      0   100%
src/reservation/service.py         34      2    94%
src/reservation/utils.py            6      0   100%
src/tables/__init__.py              0      0   100%
src/tables/exceptions.py            3      0   100%
src/tables/models.py               10      0   100%
src/tables/router.py               19      0   100%
src/tables/schemas.py              11      0   100%
src/tables/service.py              29      2    93%
src/tables/utils.py                 9      0   100%
---------------------------------------------------
TOTAL                             257     10    96%

```


## Документация API
FastAPI автоматически генерирует документацию API, которая доступна по следующим адресам:

Swagger UI: http://localhost:8000/api/v1/docs

ReDoc: http://localhost:8000/api/v1/redoc

## Логирование
Логирование настраивается через внешний файл logging.ini, который прописан в корне проекта. Логи выводятся в консоль и записываются в файл app.log. Дополнительные настройки логирования можно изменить в файле logging.ini.