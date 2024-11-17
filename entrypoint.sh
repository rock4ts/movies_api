#!/bin/bash

# Устанавливаем параметры Gunicorn
# -w: количество воркеров
# -k: используемый воркер Uvicorn для FastAPI
# --bind: адрес и порт, на которых будет запущен Gunicorn

echo "Start GUNICORN server with FastApi app Movies"

# Устанавливаем PYTHONPATH для корректного импорта
export PYTHONPATH=/app/src

exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:8000
