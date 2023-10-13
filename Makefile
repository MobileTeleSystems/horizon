#!make

include .env.local

APP_PATH = ./horizon
POETRY = ./.venv/bin/poetry

# Fix docker build and docker-compose build using different backends
COMPOSE_DOCKER_CLI_BUILD = 1
DOCKER_BUILDKIT = 1
# Fix docker build on M1/M2
DOCKER_DEFAULT_PLATFORM = linux/amd64

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

all: help

venv-init: ##@Env Init venv and install poetry dependencies
	@rm -rf .venv || true
	python3 -m venv .venv
	.venv/bin/pip install poetry
	${POETRY} config virtualenvs.create false
	${POETRY} install --no-root $(ARGS)

venv-install: ##@Env Install requirements to venv
	${POETRY} install --no-root $(ARGS)

venv-add: ##@Env Add requirement to venv
	${POETRY} add $(ARGS)

help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

db: ##@DB Start database
	docker-compose up -d db $(ARGS)

add-revision: ##@DB Generate migration file
	${POETRY} run alembic -c ./horizon/alembic.ini revision --autogenerate

upgrade: ##@DB Run migrations to head
	${POETRY} run alembic -c ./horizon/alembic.ini upgrade head

downgrade: ##@DB Downgrade head migration
	${POETRY} run alembic -c ./horizon/alembic.ini downgrade head-1

test: ##@Test Run tests
	docker-compose up -d db
	${POETRY} run pytest ./horizon/tests/ $(ARGS)

cleanup: ##@Test Cleanup tests dependencies
	docker-compose down $(ARGS)

dev: ##@Application Run development server (without docker)
	${POETRY} run uvicorn --app-dir ./horizon --factory app.main:get_application --host 0.0.0.0 --port 8000 $(ARGS)

build: ##@Application Build docker image
	docker build --progress=plain --network=host -t sregistry.mts.ru/onetools/bigdata/platform/onetools/horizon/backend:develop -f ./docker/Dockerfile.backend --target=prod $(ARGS) .

prod: ##@Application Run production server (with docker)
	docker-compose up -d

check-fixtures: ##@Test Check declared fixtures
	${POETRY} run pytest --dead-fixtures ./horizon/tests/ $(ARGS)
