# Daily USB Backup Procedure

## Objective

Create a physical end-of-day backup of Corporate Control Tower REV12 for USB storage.

## Frequency

Run once at the end of every workday after the final commit and push to GitHub.

## Command

From the repository root:

```powershell
.\scripts\backup_to_usb.ps1
```

To choose a destination manually:

```powershell
.\scripts\backup_to_usb.ps1 -DestinationRoot "E:\BIMSIG_BACKUPS"
```

## Expected Output

The script creates a ZIP with this naming pattern:

```text
corporate-control-tower-rev12_YYYYMMDD_HHMMSS_<commit>.zip
```

It also writes a SHA256 checksum file next to the ZIP:

```text
corporate-control-tower-rev12_YYYYMMDD_HHMMSS_<commit>.zip.sha256.txt
```

## End-of-Day Checklist

1. Run tests.
2. Commit all approved changes.
3. Push `main` to GitHub.
4. Connect the USB drive.
5. Run `.\scripts\backup_to_usb.ps1`.
6. Confirm the ZIP and checksum exist on the USB.
7. Eject the USB safely and store it physically.

## ADR Reference

This procedure implements ADR-0004.
