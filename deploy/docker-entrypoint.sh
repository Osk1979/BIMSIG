#!/usr/bin/env sh
set -eu

wait_for_database() {
  python - <<'PY'
import os
import sys
import time

from sqlalchemy import create_engine, text

database_url = os.environ["CONTROL_TOWER_DATABASE_URL"]
deadline = time.time() + int(os.getenv("CONTROL_TOWER_DB_WAIT_SECONDS", "60"))
last_error = None
while time.time() < deadline:
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        sys.exit(0)
    except Exception as exc:  # noqa: BLE001 - startup diagnostic
        last_error = exc
        time.sleep(2)
print(f"Database was not ready before timeout: {last_error}", file=sys.stderr)
sys.exit(1)
PY
}

if [ "${CONTROL_TOWER_WAIT_FOR_DB:-false}" = "true" ]; then
  echo "Waiting for Corporate Control Tower database..."
  wait_for_database
fi

if [ "${CONTROL_TOWER_RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "Running Corporate Control Tower database migrations..."
  alembic upgrade head
fi

exec "$@"
