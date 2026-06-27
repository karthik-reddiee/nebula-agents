# F0004-S0002 - Reflector Role and Trace Analysis

## Story Header

**Story ID:** F0004-S0002
**Feature:** F0004 - Reflective Learning Loop and Strategy Playbook
**Title:** Reflector role and trace analysis
**Priority:** High
**Phase:** Context Engineering

## User Story

**As a** framework maintainer
**I want** a reflector role that analyzes existing run evidence and emits a candidate-strategy set
**So that** recurring failure and success patterns become explicit, reusable strategy proposals instead of being lost after closeout.

## Context & Background

This story adds the analysis engine: a new `reflector` role (`agents/reflector/SKILL.md`) plus a deterministic, script-assisted analysis pass over the evidence and telemetry the framework already produces. The reflector reads run evidence, gate outcomes, and `eval.py` telemetry, then distills candidate strategies with provenance. It does not write the playbook — its only output is a candidate set handed to the `reflect` action's curation step. Programmatic analysis (a small script the role runs over telemetry) is preferred over single-pass summarization so patterns are found by recurrence, not impression.

## Acceptance Criteria

**Happy Path:**
- **Given** a completed run with evidence and telemetry
- **When** the reflector analyzes it
- **Then** it produces a candidate-strategy set where each candidate has `trigger`, `strategy`, provenance run-id(s), and a recurrence count
- **Then** the playbook artifact is unchanged (read-only on the playbook)

**Alternative Flows / Edge Cases:**
- Evidence missing or unreadable -> reflector reports insufficient input and produces zero candidates (no error-state guessing).
- A pattern appears in only one run and below the recurrence threshold -> candidate is marked low-confidence, not promoted.
- Telemetry shows a context-budget overrun -> a compression-oriented candidate is proposed referencing the offending tier.
- Evidence references a different role's scope -> candidate is tagged `cross` or routed to the owning role, not silently attributed.

## Data Requirements

**Required Fields:**
- `candidate_id`: Temporary id for the proposal.
- `source_run_ids`: Runs the candidate was distilled from.
- `pattern_kind`: e.g., `gate-reject`, `budget-overrun`, `rework`, `success`.
- `recurrence_count`: How many runs exhibit the pattern.
- `proposed_trigger`, `proposed_strategy`: Draft entry content.

**Optional Fields:**
- `confidence`: Derived from recurrence and evidence strength.
- `suggested_scope`: `framework` | `product` recommendation for curation.

**Validation Rules:**
- Every candidate cites at least one real `source_run_id`.
- The reflector never writes outside its candidate-output path.
- Provenance must be redacted of credentials before being emitted.

## Role-Based Visibility

**Roles that can run reflection:**
- Local Operator - Runs reflection on local evidence.
- Reviewer - Inspects candidate sets and provenance.
- Architect - Reviews scope recommendations before curation.

**Data Visibility:**
- InternalOnly content: raw telemetry values, local evidence paths.
- ExternalVisible content: candidate trigger/strategy summaries (domain-neutral for framework scope).

## Non-Functional Expectations

- Performance: reflection over a single run's evidence completes within a few seconds; bounded by evidence size, not whole-repo scans.
- Security: read scope honors `.agentignore` and treats `operations/**` as cold archive; authorization to read evidence matches existing evidence-contract access.
- Reliability: deterministic candidate output for identical evidence input (stable ordering and ids).

## Dependencies

**Depends On:**
- F0004-S0001 - Schema defines the shape candidates target.

**Related Stories:**
- F0004-S0003 - The reflect action consumes the candidate set.

## Business Rules

1. Read-only on the playbook: reflection proposes, it never writes.
2. Recurrence over impression: patterns are surfaced by counting across runs, not by one-shot summary.
3. Evidence-grounded: every candidate traces to real run evidence.

## Out of Scope

- Writing entries to the playbook (F0004-S0003/S0004).
- Selection or load-back (F0004-S0005).
- Defining the role's model tier beyond a recommendation in `agent-map.yaml`.

## UI/UX Notes

- No UI. The candidate set is rendered by the `reflect` action's summary view (F0004-S0003).

## Questions & Assumptions

**Open Questions:**
- [ ] What default recurrence threshold separates a low-confidence candidate from a promotable one?

**Assumptions (to be validated):**
- Existing evidence/telemetry carries enough signal (gate outcomes, token tiers, rework markers) for useful pattern detection.

## Definition of Done

- [ ] Acceptance criteria met
- [ ] Edge cases handled (missing evidence, single-run pattern, budget overrun, cross-scope attribution)
- [ ] `agents/reflector/SKILL.md` authored with scope, boundaries, and read-only-on-playbook contract
- [ ] Reflector routed in `agent-map.yaml` with a model-tier recommendation
- [ ] Permissions/authorization for evidence reads documented and honor `.agentignore`
- [ ] Tests cover candidate generation, recurrence thresholding, and zero-candidate insufficient-evidence path
- [ ] Story filename matches `Story ID` prefix
- [ ] Story index regenerated or updated

## Review Provenance

Story-level signoff provenance is recorded in the parent feature `STATUS.md`.
