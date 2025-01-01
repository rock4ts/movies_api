# Async_API_sprint_1_team

Проектная работа четвёртого спринта

https://github.com/mletunenko/Async_API_sprint_1_team


# Запуск приложения

## Docker-compose

1. Выполнить команды:
```bash
make build && make up
```

## Локальный запуск

1. Активировать venv и создать .env по образцу
2. Установить зависимости

```bash
pip install --upgrade pip && pip install -r requirements.txt
```
3. Используйте docker-compose.yml 
Так же поднятие контейнеров с сервисами для локальной работы доступны через 

```bash
make dev-build && make dev-up
```
4. Переменные окружения в конфиге по умолчанию для локального запуска.

5. Запуск приложения

```bash
cd src && fastapi dev main.py
```

# Tests

## Локальный запуск

1. Выполнить команды:

```bash
cd tests/functional && make up-dev
```
2. Запустить командой:

```bash
pytest src
```

## Запуск в docker-compose

1. Выполнить команды:

```bash
cd tests/functional && make up
```


# Docs

Наш сервис поддерживает документацию OpenAPI Swagger по адресу:

http://127.0.0.1/api/docs
