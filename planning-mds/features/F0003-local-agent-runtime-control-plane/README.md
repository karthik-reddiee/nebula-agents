# F0003 - Local Agent Runtime Control Plane

**Status:** Planned
**Priority:** High
**Phase:** Platform Hardening

## Overview

F0003 adds a concrete local runtime control plane around native agent sessions. It turns session launch, status, evidence retrieval, summarization, metrics, provider capability reports, and reviewed failure learning into explicit commands and read-only tool surfaces.

The feature does not replace native provider CLIs. It makes the surrounding Nebula runtime observable and testable so F0001 has a practical control surface and F0002 has stable contracts to build on.

## Documents

| Document | Purpose |
|----------|---------|
| [PRD.md](./PRD.md) | Full product requirements for the local runtime control plane |
| [STATUS.md](./STATUS.md) | Delivery checklist and signoff tracking |
| [GETTING-STARTED.md](./GETTING-STARTED.md) | Developer and agent setup guide |

## Stories

| ID | Title | Status |
|----|-------|--------|
| [F0003-S0001](./F0003-S0001-runtime-command-surface-and-wrap-launch.md) | Runtime command surface and wrap launch | Not Started |
| [F0003-S0002](./F0003-S0002-provider-capability-matrix-and-launch-guards.md) | Provider capability matrix and launch guards | Not Started |
| [F0003-S0003](./F0003-S0003-mcp-status-and-evidence-tools.md) | MCP status and evidence tools | Not Started |
| [F0003-S0004](./F0003-S0004-evidence-artifact-store-and-retrieval-index.md) | Evidence artifact store and retrieval index | Not Started |
| [F0003-S0005](./F0003-S0005-deterministic-transcript-log-and-validator-summaries.md) | Deterministic transcript, log, and validator summaries | Not Started |
| [F0003-S0006](./F0003-S0006-runtime-metrics-and-failure-learning-review.md) | Runtime metrics and failure-learning review | Not Started |

**Total Stories:** 6
**Completed:** 0 / 6

## Architecture Review

**Phase B status:** Drafted
**Execution Plan:** Implement as a local-only runtime layer with explicit CLI and MCP contracts.

### Key Findings

- Runtime state must be append-only or reconcilable from the actual local session state.
- Status and evidence tools should be read-only by default so agents can inspect without mutating gates.
- Summaries are navigation aids, not authoritative evidence. Full local artifacts remain retrievable by stable ID.
- Failure learning must produce proposed corrections for review, not automatic instruction edits.
