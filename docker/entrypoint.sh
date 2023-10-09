#!/usr/bin/env bash

alembic upgrade head
uvicorn --factory app.main:get_application --host 0.0.0.0 --port 8000 "$@"
