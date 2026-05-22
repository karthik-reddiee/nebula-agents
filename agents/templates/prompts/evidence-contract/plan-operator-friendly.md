Before starting, resolve `{PRODUCT_ROOT}` per `agents/docs/AGENT-USE.md` → Session Setup and echo its absolute path on your first turn; every command below assumes that resolution. This prompt encodes the plan action under the base run evidence contract from `feature-evidence-package-standardization-plan-v2.md` (effective `2026-05-19`). Plan runs BEFORE the feature evidence package exists — it produces planning artifacts in `{FEATURE_PATH}` and a base run evidence package per §8, but no feature evidence package.

Generate `{PLAN_RUN_ID}` once at session start using the contract format `YYYY-MM-DD-[a-z0-9]{8}` — date is the local date, suffix from `python3 -c "import secrets; print(secrets.token_hex(4))"`. Do not use `uuid4`. Do not regenerate after session start.

Create `PLAN_RUN_FOLDER` at `{PRODUCT_ROOT}/planning-mds/operations/evidence/{PLAN_RUN_ID}/` (note: NOT under a feature evidence root — this is the non-feature base run path per §8). Initialize base run files from templates: `README.md`, `action-context.md`, `artifact-trace.md`, `gate-decisions.md`, an empty `commands.log` (JSONL), and an empty `lifecycle-gates.log`.

Run `agents/actions/plan.md` for `FEATURE_ID={F####}` with `PHASE={A | B | A+B}`. Phase A is PM requirements; Phase B is Architect architecture; A+B runs both sequentially. Determine `FEATURE_MODE` upfront: `new` when `FEATURE_ID` is reserved in `REGISTRY.md` Planned (Reserved IDs) but `{FEATURE_PATH}` does not exist; `existing` when `{FEATURE_PATH}` already contains at least `PRD.md` and a `STATUS.md` skeleton.

Compatibility:
- `PHASE=A` + `FEATURE_MODE=new` → plan creates `{FEATURE_PATH}` and scaffolds PRD, personas, stories, and the STATUS skeleton
- `PHASE=A` + `FEATURE_MODE=existing` → plan updates existing planning artifacts; `STATUS.md` story provenance rows are append-only and must not be mutated
- `PHASE=B` + `FEATURE_MODE=new` → REJECT: cannot run architecture before requirements exist; run `PHASE=A` or `PHASE=A+B` instead
- `PHASE=B` + `FEATURE_MODE=existing` → plan updates `feature-assembly-plan.md` and ontology bindings
- `PHASE=A+B` + `FEATURE_MODE=new` → plan creates `{FEATURE_PATH}`, then runs Phase A and Phase B sequentially
- `PHASE=A+B` + `FEATURE_MODE=existing` → plan updates planning artifacts then architecture

Start only when `PLAN_RUN_FOLDER` is initialized and `python3 {PRODUCT_ROOT}/scripts/kg/validate.py` already exits 0.

Load context in this order:
1. `agents/ROUTER.md`
2. `agents/agent-map.yaml`
3. `agents/docs/AGENT-USE.md`
4. `agents/actions/plan.md`
5. `{PRODUCT_ROOT}/planning-mds/features/REGISTRY.md` (confirm `FEATURE_ID` is reserved or new)
6. `{PRODUCT_ROOT}/planning-mds/BLUEPRINT.md`
7. `{PRODUCT_ROOT}/planning-mds/knowledge-graph/solution-ontology.yaml`

Don't generate `{PLAN_RUN_ID}` with `uuid4` or any non-contract format. Don't write or consume `current-run.json`. Don't produce role reports (`g0-*`, `test-*`, `code-review-*`, etc.) — those belong to the feature action's evidence package, not the plan action. Don't create a feature evidence package at `{PRODUCT_ROOT}/planning-mds/operations/evidence/{FEATURE_ID}-{slug}/` during plan; that root is created later by `feature.md`. Don't skip the approval or ontology-sync gates. Don't edit `canonical-nodes.yaml` or `solution-ontology.yaml` outside the Architect phase.

Append every shell command to `{PLAN_RUN_FOLDER}/commands.log` as JSON Lines per the §13 schema.

Keep ownership strict:
- `product-manager` (Phase A) owns `PRD.md`, persona files, acceptance criteria, story breakdown, and the initial `STATUS.md` skeleton (Required Role Matrix and empty Story Provenance table)
- `architect` (Phase B) owns `feature-assembly-plan.md`, ADRs, API/schema updates, `canonical-nodes.yaml` updates, `solution-ontology.yaml` updates, and `feature-mappings.yaml` additions

Follow these gates exactly:
- `A0 PM REQUIREMENTS DRAFT` — produce PRD, personas, acceptance criteria, story breakdown
- `A1 PM APPROVAL GATE` — user reviews requirements; PM records decision in `gate-decisions.md`
- `B0 ARCHITECT ARCHITECTURE` — produce `feature-assembly-plan.md`, ADRs, API/schema updates, ontology bindings
- `B1 ONTOLOGY SYNC GATE` — `feature-mappings.yaml`, `canonical-nodes.yaml`, and `solution-ontology.yaml` aligned with the assembly plan; `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-drift` exit 0
- `B2 ARCHITECT APPROVAL GATE` — user reviews architecture; architect records decision in `gate-decisions.md`

Evidence outputs land in two places. In `{PLAN_RUN_FOLDER}`: the six base run files (`README.md`, `action-context.md`, `artifact-trace.md`, `gate-decisions.md`, `commands.log`, `lifecycle-gates.log`) plus an `Evidence Index` in `README.md` that points to the planning artifacts. In `{FEATURE_PATH}`: `PRD.md`, persona files, acceptance-criteria checklist, story files, `STATUS.md` skeleton (Phase A); `feature-assembly-plan.md`, ADRs, `README.md`, `GETTING-STARTED.md` (Phase B).

Stop immediately if PRD approval is refused, if architecture approval is refused, if the ontology sync gate fails and cannot be reconciled, if `kg/validate.py --check-drift` fails after one repair cycle, or if a canonical node edit is attempted outside Architect role.

Close the run by executing these in order, each exit 0:
- `python3 agents/product-manager/scripts/validate-trackers.py` (with `FEATURE_ID` context if applicable)
- `python3 agents/product-manager/scripts/generate-story-index.py {PRODUCT_ROOT}/planning-mds/features/`
- `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-drift`
- `python3 agents/scripts/validate_templates.py`

Do NOT call `validate-feature-evidence.py` at plan — there is no feature evidence package yet. The first stage validation call (`--stage G0`) happens during the feature action.

Resolve conflicts like this:
- PRD vs architecture conflict → resolve in Phase B before architecture approval; do not silently change PRD
- existing assembly plan vs new architecture → log reconciliation in `gate-decisions.md`; never silently overwrite
- ontology binding conflict → halt; resolve in `canonical-nodes.yaml` first
