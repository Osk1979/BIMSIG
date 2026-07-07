# ADR-0003: Project Provisioning as a Port

## Status

Accepted

## Context

REV11 states that Corporate Control Tower creates and registers new WEB SIG instances. Concrete provisioning technology is not specified in the available architecture documents.

## Decision

REV12 starts with a provisioning port in the application layer and a non-destructive in-memory adapter for tests and early API validation.

Real provisioning adapters for GitHub, NAS, containers, database schemas, or deployment targets require follow-up ADRs.

## Consequences

The API can expose provisioning intent and registry behavior without pretending that production infrastructure exists.
