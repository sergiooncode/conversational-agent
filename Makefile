COMPOSE_CMD = TAG=$(tag) docker compose

# Build defaults
app_env = local
target = full
tag = latest

.PHONY: up
up: .env.local
	$(COMPOSE_CMD) up -d
	sleep 1
	$(COMPOSE_CMD) ps

.PHONY: external-net
external-net: SERVICE_GRP_NET=service-grp-net
external-net:
	@if [ "$$(docker network ls --filter name=$(SERVICE_GRP_NET) --format '{{ .Name }}')" != $(SERVICE_GRP_NET) ]; then \
       docker network create $(SERVICE_GRP_NET); \
    fi

.PHONY: build
build: ## Build docker image including base dependencies
	TARGET_STAGE=$(target) $(COMPOSE_CMD) build --build-arg APP_ENV=$(app_env) $(service) --progress plain

.PHONY: check-migrations
check-migrations: ## Check for missing database migrations
	$(COMPOSE_CMD) run --rm agent-service python manage.py makemigrations --noinput --check

.PHONY: migrate
migrate: ## Run database migrations
	$(COMPOSE_CMD) run --rm agent-service sh -c "python manage.py migrate --database=default --noinput"

.PHONY: recreate
recreate: .env.local build external-net up ## Make a new clean environment including development dependencies and initial data

.PHONY: logs
logs:
	$(COMPOSE_CMD) logs -f

.PHONY: down
down:
	$(COMPOSE_CMD) down

.PHONY: linting
linting:
	$(COMPOSE_CMD) run --rm agent-service sh /opt/orbio/scripts/run-linting.sh $(fix)

.PHONY: test
test:
	$(COMPOSE_CMD) run --rm agent-service sh /opt/orbio/scripts/run-tests.sh $(name)

.PHONY: create-django-superuser
create-django-superuser:
	$(COMPOSE_CMD) run --rm agent-service python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'password') if not User.objects.filter(username='admin').exists() else print('Superuser already exists');"

.PHONY: collectstatic
collectstatic: ## Collect static files in a single location.
	$(COMPOSE_CMD) run -u 0 --rm agent-service python manage.py collectstatic --noinput

