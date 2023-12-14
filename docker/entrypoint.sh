#!/usr/bin/env bash
set -e

python -m horizon.backend.db.migrations upgrade head
python -m horizon.backend --host 0.0.0.0 --port 8000 "$@"
