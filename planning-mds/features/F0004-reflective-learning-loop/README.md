# F0004 - Reflective Learning Loop and Strategy Playbook

**Status:** Planned
**Priority:** High
**Phase:** Context Engineering

## Overview

F0004 closes the framework's context-engineering loop. Today the framework *observes* runs (telemetry, evidence, gate outcomes) but never *adapts* from them: role `SKILL.md` files are static, and the "Write" move externalizes session state and decisions without ever distilling reusable strategy, while "Select" never loads such strategy back. F0004 adds a governed `learn -> Write -> Select` sub-loop: a `reflect` action mines existing run evidence, a `reflector` role distills candidate strategies, an approval gate curates them into a scoped Strategy Playbook (`LEARNINGS.md`), and the Select/Compress moves load only task-matched, budget-bounded strategies into later sessions.

It adds the loop without breaking the three properties the framework prizes: **determinism** (every mutation is an approved diff), **boundaries** (framework vs product scope split + genericness), and the **"markdown plus small Python validators" identity** (ID/topic supersession, no vector database).

## How It Works

```text
 build / feature / review  --(evidence + telemetry)-->  reflect action
                                                            |
                              reflector role (analyze) -----+
                                                            |
                              curation (ADD/UPDATE/REMOVE/MERGE)
                                                            |
                                            APPROVAL GATE (operator)
                                                            |
                                  LEARNINGS.md  (scoped, mutable playbook)
                                                            |
                              Select + Compress (task-matched, budget-bound)
                                                            |
                                              next session's role agent
```

See [PRD.md](./PRD.md) for the full loop and approval-gate ASCII layouts, and [feature-assembly-plan.md](./feature-assembly-plan.md) for the Phase B execution plan and architecture decision.

## Documents

| Document | Purpose |
|----------|---------|
| [PRD.md](./PRD.md) | Full product requirements, loop architecture, and approval-gate layouts |
| [feature-assembly-plan.md](./feature-assembly-plan.md) | Architect Phase B execution plan, file tables, ADR, and traceability |
| [STATUS.md](./STATUS.md) | Delivery checklist and signoff tracking |
| [GETTING-STARTED.md](./GETTING-STARTED.md) | Developer and agent setup guide |

## Stories

| ID | Title | Status |
|----|-------|--------|
| [F0004-S0001](./F0004-S0001-strategy-playbook-artifact-and-schema.md) | Strategy playbook artifact and entry schema | Not Started |
| [F0004-S0002](./F0004-S0002-reflector-role-and-trace-analysis.md) | Reflector role and trace analysis | Not Started |
| [F0004-S0003](./F0004-S0003-reflect-action-and-approval-gate.md) | Reflect action and approval-gated curation | Not Started |
| [F0004-S0004](./F0004-S0004-curation-lifecycle-and-decay.md) | Curation lifecycle, counters, and supersession | Not Started |
| [F0004-S0005](./F0004-S0005-strategy-selection-and-load-back.md) | Strategy selection and context load-back | Not Started |
| [F0004-S0006](./F0004-S0006-boundary-and-genericness-gate.md) | Boundary, genericness, and lifecycle-gate enforcement | Not Started |

**Total Stories:** 6
**Completed:** 0 / 6

## Architecture Review

**Phase B status:** Drafted (see [feature-assembly-plan.md](./feature-assembly-plan.md))
**Execution Plan:** feature-assembly-plan.md

### Key Findings

- The loop is an addition to the existing four context-engineering moves, not a replacement; it reuses evidence, telemetry, `--supersedes`, genericness, and the lifecycle gate runner already in the repo.
- `LEARNINGS.md` is a new artifact deliberately kept separate from `SKILL.md`: the skill stays the static contract; the playbook holds mutable, curated strategy.
- Governance is the load-bearing design choice: approval-gated diffs, scope split, and a `learnings_governance` gate are what keep an adaptive loop compatible with a deterministic, boundary-enforced framework.
