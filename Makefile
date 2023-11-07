#!make

include .env.local

PIP = .venv/bin/pip
POETRY = .venv/bin/poetry

# Fix docker build and docker compose build using different backends
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

help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)



venv-init: venv-cleanup  venv-install##@Env Init venv and install poetry dependencies

venv-cleanup: ##@Env Cleanup venv
	@rm -rf .venv || true
	python3 -m venv .venv
	${PIP} install poetry

venv-install: ##@Env Install requirements to venv
	${POETRY} config virtualenvs.create false
	${POETRY} install --no-root --all-extras --with dev,test $(ARGS)

venv-add: ##@Env Add requirement to venv
	${POETRY} add $(ARGS)



db: db-start db-upgrade ##@DB Prepare database (in docker)

db-start: ##@DB Start database
	docker compose up -d db $(DOCKER_COMPOSE_ARGS)

db-revision: ##@DB Generate migration file
	${POETRY} run alembic -c ./horizon/alembic.ini revision --autogenerate

db-upgrade: ##@DB Run migrations to head
	${POETRY} run alembic -c ./horizon/alembic.ini upgrade head

db-downgrade: ##@DB Downgrade head migration
	${POETRY} run alembic -c ./horizon/alembic.ini downgrade head-1



test: db-start ##@Test Run tests
	${POETRY} run pytest $(PYTEST_ARGS)

check-fixtures: ##@Test Check declared fixtures
	${POETRY} run pytest --dead-fixtures $(PYTEST_ARGS)

cleanup: ##@Test Cleanup tests dependencies
	docker compose down $(ARGS)



dev: db-start ##@Application Run development server (without docker)
	${POETRY} run uvicorn --factory horizon.main:get_application --host 0.0.0.0 --port 8000 $(ARGS)

build: ##@Application Build docker image
	docker build --progress=plain --network=host -t sregistry.mts.ru/onetools/bigdata/platform/onetools/horizon/backend:develop -f ./docker/Dockerfile.backend --target=prod $(ARGS) .

prod: ##@Application Run production server (with docker)
	docker compose up -d
