[CmdletBinding()]
param(
    [string]$DestinationRoot,
    [string]$RepositoryRoot
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
    $RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Get-RepositoryCommit {
    param([string]$Root)

    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($null -eq $git) {
        $gitDirectory = Join-Path $Root ".git"
        $headPath = Join-Path $gitDirectory "HEAD"
        if (-not (Test-Path -LiteralPath $headPath)) {
            return "no-git"
        }

        $head = (Get-Content -LiteralPath $headPath -Raw).Trim()
        if ($head.StartsWith("ref: ")) {
            $ref = $head.Substring(5)
            $refPath = Join-Path $gitDirectory ($ref -replace "/", [IO.Path]::DirectorySeparatorChar)
            if (Test-Path -LiteralPath $refPath) {
                return ((Get-Content -LiteralPath $refPath -Raw).Trim()).Substring(0, 7)
            }
            $packedRefs = Join-Path $gitDirectory "packed-refs"
            if (Test-Path -LiteralPath $packedRefs) {
                $match = Get-Content -LiteralPath $packedRefs |
                    Where-Object { $_ -match "^[a-f0-9]{40}\s+$([regex]::Escape($ref))$" } |
                    Select-Object -First 1
                if ($match) {
                    return $match.Substring(0, 7)
                }
            }
            return "no-git"
        }

        if ($head -match "^[a-f0-9]{40}$") {
            return $head.Substring(0, 7)
        }

        return "no-git"
    }

    $commit = & $git.Source -C $Root rev-parse --short HEAD 2>$null
    if ([string]::IsNullOrWhiteSpace($commit)) {
        return "no-git"
    }
    return $commit.Trim()
}

function Resolve-BackupDestination {
    param([string]$RequestedDestination)

    if (-not [string]::IsNullOrWhiteSpace($RequestedDestination)) {
        New-Item -ItemType Directory -Force -Path $RequestedDestination | Out-Null
        return (Resolve-Path $RequestedDestination).Path
    }

    $usbDrive = Get-CimInstance Win32_LogicalDisk |
        Where-Object { $_.DriveType -eq 2 -and $_.FreeSpace -gt 0 } |
        Sort-Object DeviceID |
        Select-Object -First 1

    if ($null -eq $usbDrive) {
        throw "No removable USB drive was detected. Connect a USB drive or pass -DestinationRoot."
    }

    $destination = Join-Path $usbDrive.DeviceID "BIMSIG_BACKUPS"
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    return $destination
}

function Test-ExcludedPath {
    param(
        [string]$FullName,
        [string]$Root
    )

    $relative = $FullName.Substring($Root.Length).TrimStart("\", "/")
    $normalized = $relative -replace "\\", "/"

    return (
        $normalized -match "^\.venv/" -or
        $normalized -match "^__pycache__/" -or
        $normalized -match "/__pycache__/" -or
        $normalized -match "^\.pytest_cache/" -or
        $normalized -match "^\.ruff_cache/" -or
        $normalized -match "^backups/" -or
        $normalized -match "^dist/" -or
        $normalized -match "^build/" -or
        $normalized -match "\.egg-info/" -or
        $normalized -match "\.zip$"
    )
}

$repository = (Resolve-Path $RepositoryRoot).Path
$destinationRoot = Resolve-BackupDestination -RequestedDestination $DestinationRoot
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$commit = Get-RepositoryCommit -Root $repository
$backupName = "corporate-control-tower-rev12_${timestamp}_${commit}.zip"
$backupPath = Join-Path $destinationRoot $backupName

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

if (Test-Path -LiteralPath $backupPath) {
    throw "Backup already exists: $backupPath"
}

$zip = [System.IO.Compression.ZipFile]::Open($backupPath, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    Get-ChildItem -LiteralPath $repository -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object { -not (Test-ExcludedPath -FullName $_.FullName -Root $repository) } |
        ForEach-Object {
            $entryName = $_.FullName.Substring($repository.Length).TrimStart("\", "/") -replace "\\", "/"
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                $zip,
                $_.FullName,
                $entryName,
                [System.IO.Compression.CompressionLevel]::Optimal
            ) | Out-Null
        }
}
finally {
    $zip.Dispose()
}

$hash = Get-FileHash -Algorithm SHA256 -LiteralPath $backupPath
$checksumPath = "$backupPath.sha256.txt"
"$($hash.Hash)  $backupName" | Set-Content -LiteralPath $checksumPath -Encoding ascii

Write-Host "Backup created: $backupPath"
Write-Host "Checksum: $checksumPath"
