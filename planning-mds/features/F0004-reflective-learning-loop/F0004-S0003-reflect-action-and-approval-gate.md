# F0004-S0003 - Reflect Action and Approval-Gated Curation

## Story Header

**Story ID:** F0004-S0003
**Feature:** F0004 - Reflective Learning Loop and Strategy Playbook
**Title:** Reflect action and approval-gated curation
**Priority:** Critical
**Phase:** Context Engineering

## User Story

**As a** local operator
**I want** a reflect action that presents proposed playbook operations as a reviewable diff and only applies the ones I approve
**So that** the playbook can evolve from run evidence without any silent or unreviewed mutation of framework guidance.

## Context & Background

This story composes the loop into an operator-facing action (`agents/actions/reflect.md`). It runs the reflector (F0004-S0002), turns candidates into proposed curation operations (`ADD`/`UPDATE`/`REMOVE`/`MERGE`), and renders them at an approval gate. The operator can approve, hold, edit, or reject each operation; only approved operations are submitted to the curator (F0004-S0004) to apply. The action never runs inside another action's gate — it runs after a `build`/`feature`/`review` run, consistent with the framework's gate model.

## Acceptance Criteria

**Happy Path:**
- **Given** a candidate set from the reflector
- **When** the operator runs the reflect action
- **Then** proposed operations render as a diff with per-operation provenance, scope, and a budget delta
- **When** the operator approves a subset and confirms write
- **Then** only the approved operations are applied and an audit/timeline record of the approval is written

**Alternative Flows / Edge Cases:**
- Operator rejects all operations -> playbook is unchanged and the rejection is recorded.
- Genericness or scope check fails for a framework-scope operation -> that operation is blocked at the gate and cannot be approved (forbidden) until edited.
- Operator edits an operation's strategy text -> the edited form is re-validated before it can be approved.
- Approval is attempted by the same identity that authored a framework-scope promotion -> blocked; a second approver is required.
- Write fails partway -> the operation set is applied atomically or rolled back; no partial playbook.

## Interaction Contract

| Surface / Entry Point | User Action | Editable State | Save / Mutation Result | Reload / Persistence Evidence | Roles / Status Constraints |
|-----------------------|-------------|----------------|-------------------------|-------------------------------|----------------------------|
| Curation Diff Gate | Approve / hold / edit / reject each operation | Per-operation approval state and edited strategy text | Approved operations are applied to the scoped `LEARNINGS.md`; approval recorded | Re-running `validate-learnings.py` and reading the playbook shows applied entries; rejected ops leave no trace | Local Operator approves product scope; Architect required for framework-scope promotion; no self-approval |
| Reflect Summary | Open the gate from a candidate set | Read-only | None until gate confirm | Candidate set persists as evidence regardless of decision | Local Operator, Reviewer |

Required checks for mutation stories:
- [ ] Render-only behavior cannot satisfy approval; an explicit confirm-write step mutates the playbook.
- [ ] The write path validates schema, scope, and genericness before applying.
- [ ] A successful apply emits an audit/timeline record linking approver, operations, and provenance.
- [ ] Tests prove approved operations persist after reload and rejected operations do not.

## Data Requirements

**Required Fields:**
- `operation_kind`: `ADD` | `UPDATE` | `REMOVE` | `MERGE`.
- `target_strategy_id`: Entry the operation acts on (or new id for `ADD`).
- `approval_state`: `proposed` | `approved` | `held` | `rejected`.
- `approver`: Identity recording the decision.
- `provenance`: Run-id(s), action, gate outcome backing the operation.

**Optional Fields:**
- `edited_strategy`: Operator-edited text pending re-validation.
- `budget_delta`: Estimated input-budget impact of applying the operation.

**Validation Rules:**
- Only `approved` operations may be applied.
- Framework-scope promotions require an approver distinct from the author.
- Apply is atomic for the approved set.

## Role-Based Visibility

**Roles that can approve operations:**
- Local Operator - Approves product-scope operations.
- Architect - Required to approve framework-scope promotions.
- Reviewer - Can inspect and recommend hold; cannot write.

**Data Visibility:**
- InternalOnly content: approver identity details, raw provenance paths.
- ExternalVisible content: the applied strategy text and operation history.

## Non-Functional Expectations

- Performance: the gate renders proposed operations for a typical run in under 2s.
- Security: write is authorized only for approved operations; approval records are append-only and tamper-evident; no auto-approval of framework-scope promotions.
- Reliability: atomic apply with rollback on failure; deterministic diff rendering.

## Dependencies

**Depends On:**
- F0004-S0002 - Supplies the candidate set.
- F0004-S0004 - Performs the actual apply, counters, and supersession.

**Related Stories:**
- F0004-S0006 - Provides the genericness/scope gate enforced at approval time.

## Business Rules

1. No silent mutation: every playbook change is an operator-approved diff.
2. Separation of duties: framework-scope promotion needs a second approver.
3. After gates, not inside them: reflect runs post-run, never within another action's gate.

## Out of Scope

- Counter math, decay, and merge mechanics (F0004-S0004).
- Selection and load-back (F0004-S0005).
- Auto-promotion heuristics (deferred; candidate-only at launch).

## UI/UX Notes

- Screens involved: Reflect Summary, Curation Diff Gate (see PRD ASCII layouts).
- Key interactions: inspect candidate, review diff, approve/hold/edit/reject, confirm write.

## Questions & Assumptions

**Open Questions:**
- [ ] Should `held` operations persist as pending across reflect runs, or expire after a fixed window?

**Assumptions (to be validated):**
- Operators prefer per-operation approval over all-or-nothing for early adoption.

## Definition of Done

- [ ] Acceptance criteria met
- [ ] Mutation interaction contract satisfied and not closable by render-only behavior
- [ ] Edge cases handled (reject-all, blocked op, edited op re-validation, self-approval block, atomic rollback)
- [ ] `agents/actions/reflect.md` authored and catalogued in `agents/actions/README.md`
- [ ] Approval/authorization rules enforced (second approver for framework scope)
- [ ] Audit/timeline record written for every apply and rejection
- [ ] Tests cover approve-subset, reject-all, blocked-by-gate, edit-then-approve, and atomic-rollback
- [ ] Story filename matches `Story ID` prefix
- [ ] Story index regenerated or updated

## Review Provenance

Story-level signoff provenance is recorded in the parent feature `STATUS.md`.
