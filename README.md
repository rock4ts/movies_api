# Async_API_sprint_1_team

Проектная работа четвёртого спринта


# Запуск приложения

## Docker-compose

1. Создать .env по образцу
2. Выполнить команды:
```bash
make build && make up
```

## Локальный запуск

1. Активировать venv и создать .env по образцу
2. Установить зависимости
```bash
pip install --upgrade pip && pip install -r requirements.txt
```
3. Запуск приложения

```bash
cd src && fastapi dev main.py
```

# Docs

Наш сервис поддерживает документацию OpenAPI Swagger по адресу:

http://127.0.0.1:8000/api/openapi
