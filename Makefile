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
external-net: ## Create common external docker network (if missing).
    # this network is shared across services and marked as external in docker compose (thus not managed by it).
    @if["$$(docker network ls --filter name=$(SERVICE_GRP_NET) --format '{{ .Name }}')" != $(SERVICE_GRP_NET) ]; then \
       docker network create $(SERVICE_GRP_NET); \
    fi

.PHONY: build
build: ## Build docker image including base dependencies
	TARGET_STAGE=$(target) $(COMPOSE_CMD) build --build-arg APP_ENV=$(app_env) $(service)

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
