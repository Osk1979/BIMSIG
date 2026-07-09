# PROMPT HARDENING-008 - Visual E2E Testing

ADR references:
- ADR-0018: Corporate executive dashboard.
- ADR-0021: DevSecOps operating model.
- ADR-0024: Corporate operating model.
- ADR-0031: Corporate Experience Platform.

## Objective

Validate the Enterprise user experience from a real browser with Playwright, screenshots, responsive viewports, dark/light mode, and anti-overlap checks.

## Delivered

- Playwright optional dependency for E2E testing:
  - `.[e2e]`
- Visual E2E test suite:
  - `tests/e2e/test_visual_experience.py`
- Browser-tested flows:
  - Dashboard.
  - Portfolio Explorer.
  - Corporate GIS Dashboard.
  - Enterprise Wizard.
  - Corporate Reporting.
- Viewports:
  - Desktop: `1440x1000`.
  - Laptop: `1366x768`.
  - Tablet: `1024x768`.
- Visual screenshots written to:
  - `e2e-artifacts/`
- Anti-overlap validation for key controls and cards.
- Dark/light mode validation.
- CI job:
  - Installs Playwright Chromium.
  - Runs `python -m pytest tests/e2e`.
  - Uploads visual screenshots as artifacts.
- Dashboard now exposes a Corporate Reporting visual panel backed by existing report preview endpoints.

## Guardrails

- No WEB SIG operational logic was added.
- No geometry editing or field capture was introduced.
- Visual tests run against a temporary SQLite database and seed only controlled demo data.
- Local environments without Playwright skip E2E tests; CI installs and executes them.
