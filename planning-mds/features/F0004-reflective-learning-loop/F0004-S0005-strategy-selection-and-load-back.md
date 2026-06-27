# F0004-S0005 - Strategy Selection and Context Load-Back

## Story Header

**Story ID:** F0004-S0005
**Feature:** F0004 - Reflective Learning Loop and Strategy Playbook
**Title:** Strategy selection and context load-back
**Priority:** High
**Phase:** Context Engineering

## User Story

**As a** role agent starting a session
**I want** only the strategies relevant to my task loaded into my context within the input budget
**So that** I benefit from learned strategy without busting the cache or exceeding the context budget.

## Context & Background

A playbook is only useful if the right entries reach the next agent cheaply. This story implements the Select/Compress half of the loop: `playbook.py select --role --task` returns task-matched strategies, integrated with `ROUTER.md` task routing and placed in the stable cache tiers (not the per-turn tail), respecting the §13.3 input budget. It also records selection so the curator's counters stay accurate. Selection is a retrieval aid: on conflict the role `SKILL.md` contract wins, consistent with KG source precedence.

## Acceptance Criteria

**Happy Path:**
- **Given** an active playbook and a task summary
- **When** a role agent selects strategies at session start
- **Then** only entries whose `trigger` matches the task/role are returned, ordered by relevance and success rate
- **Then** the returned slice fits within the configured share of the input budget and is placed in a stable cache tier

**Alternative Flows / Edge Cases:**
- No entry matches the task -> empty selection; the agent proceeds with its `SKILL.md` contract only (no error).
- Matched set exceeds the budget share -> lowest-value entries are dropped to fit and the drop is reported, not silently truncated mid-entry.
- A selected strategy conflicts with the `SKILL.md` contract -> the contract wins and the conflict is flagged for reflection.
- Selection requested for a role with load-back disabled -> returns empty with a disabled notice.
- Stale/superseded entries are never selected (only `active`).

## Interaction Contract

| Surface / Entry Point | User Action | Editable State | Save / Mutation Result | Reload / Persistence Evidence | Roles / Status Constraints |
|-----------------------|-------------|----------------|-------------------------|-------------------------------|----------------------------|
| `playbook.py select` | Select strategies for a session | None on the playbook content | Increments `used_count`/`last_used` via `record-outcome` for selected entries | Counter increments persist and reconcile with the session run-id | Read-only on strategy text; only counters mutate, through the curator |

Required checks for mutation stories:
- [ ] Render-only selection cannot alter strategy content; only counters update via the curator.
- [ ] Selection validates budget fit before returning.
- [ ] A selection event has an audit/timeline link to the consuming session run-id.
- [ ] Tests prove counters increment on selection and superseded entries are excluded.

## Data Requirements

**Required Fields:**
- `role`, `task`: Selection inputs.
- `selected_ids`: Entries returned.
- `budget_share`: Fraction of input budget consumed by the slice.
- `dropped_ids`: Entries cut to fit budget.

**Optional Fields:**
- `relevance_score`: Trigger-match strength used for ordering.
- `tier_placement`: Which cache tier the slice loaded into.

**Validation Rules:**
- Only `active` entries are eligible.
- Selection must not exceed `NEBULA_AGENTS_LEARNING_BUDGET_PCT` of the input budget.
- Selection is deterministic for identical playbook + task inputs.

## Role-Based Visibility

**Roles that consume selection:**
- Role Agents - Receive selected strategies read-only at session start.
- Local Operator - Can preview a selection for a task without starting a session.
- Architect - Approves budget-share and selection thresholds.

**Data Visibility:**
- InternalOnly content: relevance scoring internals and tier placement.
- ExternalVisible content: the selected strategy text shown in the prompt.

## Non-Functional Expectations

- Performance: selection resolves in under 1s and adds no per-turn cache-write spike (load-back lands in a stable tier).
- Security: selection is read-only on content; authorization to read the playbook matches role read scopes; no cross-scope leakage (a role sees only its scope plus `cross`).
- Reliability: deterministic, budget-bounded output; superseded/retired entries are never surfaced.

## Dependencies

**Depends On:**
- F0004-S0001 - Entry schema and status.
- F0004-S0004 - Counter updates via `record-outcome`.

**Related Stories:**
- F0004-S0002 - Budget overruns observed here feed future reflection candidates.

## Business Rules

1. Task-matched, not whole-file: selection loads a slice, never the entire playbook.
2. Stable tier only: load-back never enters the per-turn tail and never busts the cached prefix.
3. Contract wins: on conflict, `SKILL.md` overrides a selected strategy.

## Out of Scope

- Reflection and curation (earlier stories).
- Genericness/scope gate (F0004-S0006).
- Cross-workspace or shared selection.

## UI/UX Notes

- Screens involved: Playbook Inspector (preview a selection).
- Key interactions: preview selection for a task, inspect budget share and drops.

## Questions & Assumptions

**Open Questions:**
- [ ] Should relevance ordering weight `success_count` over recency, or blend both?

**Assumptions (to be validated):**
- Trigger-based matching plus `ROUTER.md` routing is precise enough without semantic embeddings at expected sizes.

## Definition of Done

- [ ] Acceptance criteria met
- [ ] Edge cases handled (no match, over-budget drop, contract conflict, disabled role, superseded exclusion)
- [ ] `playbook.py select` implemented and integrated with `ROUTER.md` and cache tiers
- [ ] Budget bound enforced and measured against §13.3 input budget
- [ ] Selection records counters via the curator and links to the session run-id
- [ ] Authorization limits a role to its own scope plus `cross`
- [ ] Tests cover match, no-match, budget drop, conflict flag, and counter increment
- [ ] Story filename matches `Story ID` prefix
- [ ] Story index regenerated or updated

## Review Provenance

Story-level signoff provenance is recorded in the parent feature `STATUS.md`.
