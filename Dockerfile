# Базовый образ Python
FROM python:3.10

# Установим рабочую директорию
WORKDIR /app

# Скопируем файлы зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

# Скопируем код приложения в рабочую директорию
COPY . .

# Скопируем скрипт entrypoint
COPY entrypoint.sh /app/entrypoint.sh

# Дадим права на выполнение скрипта
RUN chmod +x /app/entrypoint.sh

# Устанавливаем скрипт как точку входа
ENTRYPOINT ["/app/entrypoint.sh"]
