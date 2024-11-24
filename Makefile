# Сборка контейнера
build:
	docker-compose build

# Запуск контейнера
up:
	docker-compose up -d

logs:
	docker-compose logs

# Остановка контейнера
down:
	docker-compose down

full-down:
	docker-compose down --volumes --remove-orphans

clear:
	docker system prune


# Для локального запуска docker и приложения
dev-build:
	docker-compose -f 'docker-compose-dev.yml' build

dev-logs:
	docker-compose -f 'docker-compose-dev.yml' logs

dev-up:
	docker-compose -f 'docker-compose-dev.yml' up -d

dev-down:
	docker-compose -f 'docker-compose-dev.yml' down

dev-full-down:
	docker-compose -f 'docker-compose-dev.yml' down --volumes --remove-orphans
