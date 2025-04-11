# Этап сборки
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements/prod.txt requirements/
RUN pip install --upgrade pip && \
    pip install -r requirements/prod.txt --no-cache-dir --user

# Финальный этап
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY . .

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}"


ENTRYPOINT ["/app/entrypoint.sh"]