#!/usr/bin/env sh
set -eu

DESTINATION="${1:-/srv/bimsig/backups/control-tower}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.production}"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
BACKUP_DIR="${DESTINATION}/${STAMP}"

mkdir -p "${BACKUP_DIR}"

echo "Creating Corporate Control Tower production backup at ${BACKUP_DIR}"

if [ -f "${ENV_FILE}" ]; then
  cp "${ENV_FILE}" "${BACKUP_DIR}/env.production.redacted"
  sed -i 's/PASSWORD=.*/PASSWORD=REDACTED/g; s/SECRET=.*/SECRET=REDACTED/g; s/TOKEN=.*/TOKEN=REDACTED/g' \
    "${BACKUP_DIR}/env.production.redacted"
fi

docker compose -f "${COMPOSE_FILE}" exec -T postgis \
  pg_dump -U "${POSTGRES_USER:-controltower}" "${POSTGRES_DB:-controltower}" \
  > "${BACKUP_DIR}/postgis_${STAMP}.sql"

docker compose -f "${COMPOSE_FILE}" exec -T control-tower \
  python - <<'PY' > "${BACKUP_DIR}/operational_health.json"
import json
import urllib.request

with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/observability/dashboard", timeout=10) as response:
    print(json.dumps(json.loads(response.read()), indent=2, sort_keys=True))
PY

if [ -d "${CONTROL_TOWER_NAS_HOST_PATH:-./runtime/nas}" ]; then
  tar -czf "${BACKUP_DIR}/nas_runtime_${STAMP}.tar.gz" "${CONTROL_TOWER_NAS_HOST_PATH:-./runtime/nas}"
fi

tar -czf "${BACKUP_DIR}/control_tower_contracts_${STAMP}.tar.gz" docs/api docs/operations docs/adr

find "${BACKUP_DIR}" -type f ! -name SHA256SUMS -print0 | xargs -0 sha256sum > "${BACKUP_DIR}/SHA256SUMS"

echo "Backup completed: ${BACKUP_DIR}"
