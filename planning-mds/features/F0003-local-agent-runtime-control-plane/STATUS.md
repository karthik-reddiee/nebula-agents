# F0003 - Local Agent Runtime Control Plane - Status

**Overall Status:** Draft
**Last Updated:** 2026-06-24

## Story Checklist

| Story | Title | Status |
|-------|-------|--------|
| F0003-S0001 | Runtime command surface and wrap launch | [ ] Not Started |
| F0003-S0002 | Provider capability matrix and launch guards | [ ] Not Started |
| F0003-S0003 | MCP status and evidence tools | [ ] Not Started |
| F0003-S0004 | Evidence artifact store and retrieval index | [ ] Not Started |
| F0003-S0005 | Deterministic transcript, log, and validator summaries | [ ] Not Started |
| F0003-S0006 | Runtime metrics and failure-learning review | [ ] Not Started |

## Runtime Progress

- [ ] Local command surface implemented
- [ ] Wrapped launch records run metadata
- [ ] Session status reconciles against real local session state
- [ ] Provider capability reports and launch guards implemented
- [ ] MCP read-only status tools implemented
- [ ] Evidence artifact store and retrieval index implemented
- [ ] Deterministic summarizers implemented
- [ ] Metrics dashboard or status view implemented
- [ ] Failure-learning proposal review flow implemented

## Cross-Cutting

- [ ] Story validator passes
- [ ] Tracker validator passes
- [ ] Security review of redaction and retrieval boundaries completed
- [ ] Architecture review of runtime contract completed
- [ ] Tests cover command surface, MCP tools, artifact retrieval, summaries, metrics, and proposal workflow

## Required Signoff Roles (Set in Planning)

| Role | Required | Why Required | Set By | Date |
|------|----------|--------------|--------|------|
| Quality Engineer | Yes | Validates command behavior, status contracts, artifact retrieval, summaries, and metrics. | Architect | 2026-06-24 |
| Code Reviewer | Yes | Reviews runtime command implementation, tool contracts, and persistence boundaries. | Architect | 2026-06-24 |
| Security Reviewer | Yes | Reviews redaction, local path constraints, MCP read-only boundaries, and proposal safety. | Architect | 2026-06-24 |
| DevOps | No | Local-only runtime layer unless a later feature adds hosted operation. | Architect | 2026-06-24 |
| Architect | Yes | Required for runtime contract and F0002 handoff approval. | Architect | 2026-06-24 |

## Story Signoff Provenance

Complete this before moving `Overall Status` to `Done` or `Archived`.

| Story | Role | Reviewer | Verdict | Evidence | Date | Notes |
|-------|------|----------|---------|----------|------|-------|
| F0003-S0001 | Quality Engineer | TBD | TBD | TBD | TBD | Pending implementation |
| F0003-S0001 | Code Reviewer | TBD | TBD | TBD | TBD | Pending implementation |
| F0003-S0001 | Security Reviewer | TBD | TBD | TBD | TBD | Pending implementation |
| F0003-S0001 | Architect | TBD | TBD | TBD | TBD | Pending implementation |

## Deferred Non-Blocking Follow-ups

| Follow-up | Why deferred | Tracking link | Owner |
|-----------|--------------|---------------|-------|

## Closeout Summary

| Field | Value |
|-------|-------|
| Implementation completed | TBD |
| Closeout review date | TBD |
| Total stories | 6 |
| Stories completed | 0 / 6 |
| Test count (unit + integration) | TBD |
| Defects found during review | TBD |
| Defects fixed before closeout | TBD |
| Residual risks | TBD |

## Tracker Sync Checklist

- [ ] `planning-mds/features/REGISTRY.md` status/path aligned
- [ ] `planning-mds/features/ROADMAP.md` section aligned
- [ ] `planning-mds/features/STORY-INDEX.md` regenerated or updated
- [ ] `planning-mds/BLUEPRINT.md` feature/story status links aligned if applicable
- [ ] Every required signoff role has story-level `PASS` entries with reviewer, date, and evidence
