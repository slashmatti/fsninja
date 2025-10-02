# Variables
DOCKER_COMPOSE = docker-compose

# Build and start containers
up:
	$(DOCKER_COMPOSE) up --build

# Stop containers and remove volumes (optional safety)
down:
	$(DOCKER_COMPOSE) down -v

# Run database migrations
migrate:
	$(DOCKER_COMPOSE) run --rm web python manage.py migrate

# Run tests
test:
	$(DOCKER_COMPOSE) run --rm web python manage.py test

# Seed database with initial data
seed:
	$(DOCKER_COMPOSE) run --rm web python manage.py load_readings seed/sensor_readings_wide.csv
