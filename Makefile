.PHONY: up down build rebuild logs ps test clean

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

rebuild:
	docker-compose down -v
	docker-compose up --build -d

logs:
	docker-compose logs -f

ps:
	docker-compose ps

test:
	docker-compose run --rm web pytest

migrate:
	docker-compose run --rm web python manage.py migrate

makemigrations:
	docker-compose run --rm web python manage.py makemigrations

createsuperuser:
	docker-compose run --rm web python manage.py createsuperuser

shell:
	docker-compose run --rm web python manage.py shell_plus

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Production commands
prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

prod-ps:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Database backup
backup:
	docker-compose exec db pg_dump -U $$(grep DB_USER .env | cut -d '=' -f2) -d $$(grep DB_NAME .env | cut -d '=' -f2) > backup_$$(date +%Y%m%d_%H%M%S).sql

# Database restore
restore:
	@if [ -z "$(file)" ]; then \
		echo "Usage: make restore file=backup_file.sql"; \
		exit 1; \
	fi
	docker-compose exec -T db psql -U $$(grep DB_USER .env | cut -d '=' -f2) -d $$(grep DB_NAME .env | cut -d '=' -f2) < $(file)
