param(
    [string]$PythonPath = "python",
    [string]$GitPath = "git",
    [string]$DockerPath = "docker",
    [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"

Write-Host "Running ruff"
& $PythonPath -m ruff check .

Write-Host "Exporting OpenAPI"
& $PythonPath scripts/export_openapi.py

Write-Host "Running tests"
& $PythonPath -m pytest

Write-Host "Checking git diff"
& $GitPath diff --check

if (-not $SkipDocker) {
    Write-Host "Building Docker image"
    & $DockerPath build -t corporate-control-tower-rev12:local .
}

Write-Host "Release check completed"
