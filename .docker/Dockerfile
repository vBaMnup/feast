# Этап сборки
FROM python:3.12-slim AS builder

# Установка инструментов для сборки и их удаление после использования
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей
WORKDIR /app
COPY requirements/prod.txt requirements/
RUN pip install --upgrade pip && \
    pip install -r requirements/prod.txt --no-cache-dir --user

# Финальный этап
FROM python:3.12-slim

# Установка рабочей директории
WORKDIR /app

# Копирование только необходимых файлов
COPY --from=builder /root/.local /home/appuser/.local
COPY ./src ./src

# Создание непривилегированного пользователя
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

# Переключение на непривилегированного пользователя
USER appuser

# Открытие порта
EXPOSE 8000

# Настройка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}"


# Запуск приложения через Uvicorn с оптимизацией
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]