# Architecture Verification Checklist

## Mandatory Before Code

1. Read ADR-0001 and confirm the Master Architecture baseline still applies.
2. Confirm the change belongs inside Corporate Control Tower REV12.
3. Confirm the change does not create an independent WEB SIG, BIMSIG Field, GeoServer, or NAS app.
4. Confirm company and project scope is explicit for project-related data.
5. Confirm integration goes through existing ports, adapters, or approved new ports.
6. Confirm the Tower consumes consolidated information and does not operate project workflows directly.
7. Confirm scalability for hundreds of simultaneous projects.
8. Confirm a relevant ADR is referenced or create a new ADR.
9. Confirm backlog and traceability are updated.
10. Run `python scripts/validate_architecture.py`.

## Required Integration Review

- Corporate Control Tower.
- WEB SIG Factory.
- Project Provisioning Engine.
- PostGIS.
- GeoServer.
- NAS.
- Google Workspace.
- BIMSIG Field.

## Release Gate

Architecture guardrails must pass before release:

```powershell
python scripts/validate_architecture.py
```
