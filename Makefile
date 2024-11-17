# Сборка контейнера
build:
	docker-compose build

# Запуск контейнера
up:
	docker-compose up -d

# Остановка контейнера
down:
	docker-compose down

full-down:
	docker-compose down --volumes --remove-orphans

clear:
	docker system prune