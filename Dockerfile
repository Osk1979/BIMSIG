FROM python:3.12-slim

LABEL org.opencontainers.image.title="Corporate Control Tower REV12"
LABEL org.opencontainers.image.description="BIMSIG Enterprise Corporate Control Tower API"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CONTROL_TOWER_DATABASE_URL=sqlite:////data/control_tower.db
ENV CONTROL_TOWER_NAS_ROOT=/mnt/nas
ENV CONTROL_TOWER_REPORT_OUTPUT_DIR=/app/output/pdf
ENV CONTROL_TOWER_RUN_MIGRATIONS=false
ENV CONTROL_TOWER_WAIT_FOR_DB=false

WORKDIR /app

RUN addgroup --system controltower && adduser --system --ingroup controltower controltower

RUN mkdir -p /app/docs/api /app/output /mnt/nas

COPY pyproject.toml README.md alembic.ini ./
COPY migrations ./migrations
COPY src ./src
COPY docs/api/openapi.yaml ./docs/api/openapi.yaml
COPY deploy/docker-entrypoint.sh /usr/local/bin/control-tower-entrypoint.sh

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir .

RUN chmod +x /usr/local/bin/control-tower-entrypoint.sh \
    && mkdir -p /data /mnt/nas /app/output \
    && chown -R controltower:controltower /app /data /mnt/nas

USER controltower

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/operational/readiness', timeout=3).read()"

ENTRYPOINT ["control-tower-entrypoint.sh"]
CMD ["uvicorn", "control_tower.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
