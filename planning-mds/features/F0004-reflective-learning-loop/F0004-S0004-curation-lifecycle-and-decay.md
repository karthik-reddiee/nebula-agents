# F0004-S0004 - Curation Lifecycle, Counters, and Supersession

## Story Header

**Story ID:** F0004-S0004
**Feature:** F0004 - Reflective Learning Loop and Strategy Playbook
**Title:** Curation lifecycle, counters, and supersession
**Priority:** High
**Phase:** Context Engineering

## User Story

**As a** framework maintainer
**I want** the curator to apply approved operations, maintain usage and success counters, and retire stale or failing strategies
**So that** the playbook stays small, current, and trustworthy instead of growing without bound.

## Context & Background

This story implements the curator (`agents/scripts/playbook.py`) that the reflect action calls to apply approved operations. It performs `ADD`/`UPDATE`/`REMOVE`/`MERGE`, maintains `used_count` and `success_count`, decays entries that are never selected or repeatedly unsuccessful, and supersedes prior entries by ID/topic — reusing the existing `workstate.py decision --supersedes` current-view semantics rather than introducing embeddings or a vector store.

## Acceptance Criteria

**Happy Path:**
- **Given** an approved operation set
- **When** the curator applies it
- **Then** entries are created/updated/removed/merged per the operations and the file re-validates
- **When** a strategy is selected and a later run records its outcome
- **Then** `used_count` increments on selection and `success_count` increments on a positive gate outcome

**Alternative Flows / Edge Cases:**
- `MERGE` of two near-duplicate entries -> one survivor accumulates both counters; the other is set `superseded` with `supersedes` linkage (audited).
- Decay threshold reached (e.g., `used_count = 0` over N runs) -> entry proposed for `retired`, not hard-deleted, preserving history.
- Conflicting concurrent updates to the same entry -> last-writer rejected; operator must re-run against current state.
- `UPDATE` that would change an entry's scope -> rejected; scope changes require a new id, not an in-place mutation.
- Counter update references a retired entry -> ignored and logged.

## Interaction Contract

| Surface / Entry Point | User Action | Editable State | Save / Mutation Result | Reload / Persistence Evidence | Roles / Status Constraints |
|-----------------------|-------------|----------------|-------------------------|-------------------------------|----------------------------|
| `playbook.py apply` | Apply approved operations | Entry fields, status, counters, supersedes linkage | Scoped `LEARNINGS.md` updated; superseded entries marked, not erased | `validate-learnings.py` passes and `--current-view` shows only active entries | Invoked only by the reflect action after gate approval |
| `playbook.py record-outcome` | Record selection/outcome | `used_count`, `success_count`, `last_used` | Counters incremented append-only | Counter values persist and reconcile with run evidence | Invoked by the runtime when a selected strategy is used |

Required checks for mutation stories:
- [ ] Render-only behavior cannot satisfy curation; the apply path mutates and re-validates the playbook.
- [ ] Counter and status changes are append-only and traceable to an approved operation or a recorded outcome.
- [ ] Supersession preserves history (mark, do not delete) and is shown in an audit/timeline record.
- [ ] Tests prove merged counters accumulate and retired entries persist with history after reload.

## Data Requirements

**Required Fields:**
- `operation_kind`, `target_strategy_id`: From the approved operation.
- `used_count`, `success_count`, `last_used`: Maintained counters.
- `status`: Transitions among `candidate`/`active`/`superseded`/`retired`.
- `supersedes`: Linkage set on merge/replace.

**Optional Fields:**
- `decay_reason`: Why an entry was proposed for retirement.
- `merge_sources`: Ids merged into a survivor.

**Validation Rules:**
- Counters are monotonic non-negative and only change via `record-outcome` or `MERGE` accumulation.
- Retirement is reversible only by a new approved `ADD`, not by editing a retired entry.
- Scope is immutable per entry; a scope change is a new id.

## Role-Based Visibility

**Roles that can curate:**
- Local Operator - Triggers apply via the approved gate output.
- Architect - Approves decay/retirement thresholds.
- Reviewer - Inspects counter and supersession history.

**Data Visibility:**
- InternalOnly content: raw counter telemetry and merge bookkeeping.
- ExternalVisible content: current active strategies and their status.

## Non-Functional Expectations

- Performance: apply and `--current-view` resolve in under 2s for a 200-entry playbook.
- Security: only the gated apply path may mutate the playbook; authorization mirrors framework file-write boundaries; no unauthenticated counter writes.
- Reliability: atomic apply with rollback; deterministic supersession resolution.

## Dependencies

**Depends On:**
- F0004-S0001 - Schema for entries and statuses.
- F0004-S0003 - Supplies approved operations.

**Related Stories:**
- F0004-S0005 - Selection increments counters via `record-outcome`.

## Business Rules

1. Mark, do not delete: superseded and retired entries keep history for audit.
2. Reuse supersession: ID/topic `--supersedes` semantics replace embeddings.
3. Immutable scope: scope changes require a new id, never an in-place edit.

## Out of Scope

- Selection and budget logic (F0004-S0005).
- Genericness enforcement (F0004-S0006).
- Reflection/candidate generation (F0004-S0002).

## UI/UX Notes

- No new UI; curation results surface in the Playbook Inspector and the curation gate audit trail.

## Questions & Assumptions

**Open Questions:**
- [ ] What default `used_count`/window pair triggers a retirement proposal without churning useful-but-rare strategies?

**Assumptions (to be validated):**
- ID/topic supersession is sufficient dedup at expected playbook sizes (low hundreds of entries).

## Definition of Done

- [ ] Acceptance criteria met
- [ ] Mutation interaction contract satisfied and not closable by render-only behavior
- [ ] Edge cases handled (merge accumulation, decay-to-retire, concurrent update, scope-change rejection, retired-entry counter)
- [ ] `playbook.py` curator implements apply/record-outcome/merge/supersede/decay
- [ ] Authorization restricts mutation to the gated apply path
- [ ] Audit/timeline records written for apply, merge, and retirement
- [ ] Tests cover apply, counter increments, merge, decay, supersession, and atomic rollback
- [ ] Story filename matches `Story ID` prefix
- [ ] Story index regenerated or updated

## Review Provenance

Story-level signoff provenance is recorded in the parent feature `STATUS.md`.
