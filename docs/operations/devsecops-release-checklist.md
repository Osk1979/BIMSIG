# DevSecOps Release Checklist

## Purpose

Prepare a controlled Corporate Control Tower REV12 release.

## Required Checks

1. Confirm working tree is clean before release work.
2. Run `python -m ruff check .`.
3. Run `python scripts/export_openapi.py`.
4. Run `python -m pytest`.
5. Run `git diff --check`.
6. Build the Docker image with `docker build -t corporate-control-tower-rev12:local .`.
7. Confirm `/api/v1/operational/readiness` returns `ready`.
8. Confirm `/api/v1/operational/version` matches the release version.
9. Commit and push to GitHub.
10. Create the end-of-day USB backup according to `docs/operations/daily-usb-backup.md`.

## Helper Script

```powershell
.\scripts\release_check.ps1
```

Use this local option when Docker is not available:

```powershell
.\scripts\release_check.ps1 -SkipDocker
```

Use explicit tool paths when the terminal does not expose `python` or `git` in `PATH`:

```powershell
.\scripts\release_check.ps1 -SkipDocker -PythonPath "C:\Path\To\python.exe" -GitPath "C:\Path\To\git.exe"
```

## Release Rule

No production release is accepted unless code, tests, OpenAPI, ADRs, backlog, GitHub push, and USB
backup are complete.
