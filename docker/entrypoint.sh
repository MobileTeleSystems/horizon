#!/usr/bin/env bash
set -e

python -m horizon.backend.db.migrations upgrade head

# user only by entrypoint
if [[ "x${HORIZON__ENTRYPOINT__ADMIN_USERS}" != "x" ]]; then
  admins=$(echo "${HORIZON__ENTRYPOINT__ADMIN_USERS}" | tr "," " ")
  python -m horizon.backend.scripts.manage_admins add ${admins}
  python -m horizon.backend.scripts.manage_admins list
fi

exec python -m horizon.backend --host 0.0.0.0 --port 8000 "$@"
