# feast

Запуск Docker-compose:

```bash
docker compose -f .docker/docker-compose.yml --env-file .docker/.db.env up -d --build --force-recreate 
```

Тесты с покрытием:

```bash
pytest --cov=src tests/
```