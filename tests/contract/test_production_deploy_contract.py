from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_production_dockerfile_contract() -> None:
    dockerfile = read("Dockerfile")

    assert "USER controltower" in dockerfile
    assert "CONTROL_TOWER_NAS_ROOT=/mnt/nas" in dockerfile
    assert "CONTROL_TOWER_RUN_MIGRATIONS=false" in dockerfile
    assert "ENTRYPOINT" in dockerfile
    assert "/api/v1/operational/readiness" in dockerfile


def test_production_compose_contract() -> None:
    compose = read("docker-compose.prod.yml")

    assert "control-tower:" in compose
    assert "postgis:" in compose
    assert "reverse-proxy:" in compose
    assert "CONTROL_TOWER_RUN_MIGRATIONS" in compose
    assert "CONTROL_TOWER_NAS_HOST_PATH" in compose
    assert "condition: service_healthy" in compose
    assert "postgis/postgis" in compose


def test_production_environment_template_has_no_real_secret() -> None:
    env_template = read(".env.production.example")

    assert "CONTROL_TOWER_AUTH_SECRET=replace-with-strong-random-secret" in env_template
    assert "POSTGRES_PASSWORD=change-me" in env_template
    assert ".env.production" in read(".gitignore")
    assert "!.env.production.example" in read(".gitignore")


def test_production_reverse_proxy_and_backup_contract() -> None:
    nginx = read("deploy/nginx/conf.d/control-tower.conf")
    backup = read("scripts/production_backup.sh")
    runbook = read("docs/operations/production-deploy-runbook.md")

    assert "proxy_set_header X-Request-ID" in nginx
    assert "pg_dump" in backup
    assert "SHA256SUMS" in backup
    assert "CONTROL_TOWER_RUN_MIGRATIONS=true" in runbook
    assert "scripts/production_backup.sh" in runbook
