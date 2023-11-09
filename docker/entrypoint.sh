#!/usr/bin/env bash

alembic -c ./horizon/backend/alembic.ini upgrade head
uvicorn --factory horizon.backend.main:get_application --host 0.0.0.0 --port 8000 "$@"
