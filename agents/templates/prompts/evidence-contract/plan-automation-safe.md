ACTION: agents/actions/plan.md
CONTRACT: feature-evidence-package-standardization-plan-v2.md (effective 2026-05-19)
CONTRACT SCOPE: Plan runs BEFORE the feature evidence package exists. It produces planning artifacts (feature-assembly-plan.md, PRD updates, ADRs, story breakdowns) inside {FEATURE_PATH}. It also produces a base run evidence package per §8 at the non-feature run path.

SESSION_SETUP:
- Resolve {PRODUCT_ROOT} per agents/docs/AGENT-USE.md → Session Setup
- Echo the resolved absolute {PRODUCT_ROOT} path on the first turn before any shell command
- Generate {PLAN_RUN_ID} once at session start using the contract format:
    date  = local date in ISO YYYY-MM-DD
    suffix = `python3 -c "import secrets; print(secrets.token_hex(4))"`
    PLAN_RUN_ID = {date}-{suffix}
  DO NOT use uuid4. DO NOT regenerate {PLAN_RUN_ID} after session start.
- Create base run folder per §8 (non-feature profile):
    PLAN_RUN_FOLDER = {PRODUCT_ROOT}/planning-mds/operations/evidence/{PLAN_RUN_ID}/
    mkdir -p {PLAN_RUN_FOLDER}
- Initialize base run files from templates: README.md, action-context.md, artifact-trace.md, gate-decisions.md, commands.log (empty JSONL), lifecycle-gates.log (empty)
- Plan runs do NOT create a feature evidence package. The feature evidence root is created later by `agents/actions/feature.md` for the same FEATURE_ID.

PARAMETERS:
  FEATURE_ID:    {F####}
  FEATURE_PATH:  {PRODUCT_ROOT}/planning-mds/features/{F####-slug}      # POSIX (created during plan if new)
  PLAN_RUN_ID:   {YYYY-MM-DD-[a-z0-9]{8}; generated per SESSION_SETUP}
  PHASE:         {A | B | A+B}   # A = PM requirements; B = Architect architecture; A+B = both

PRECONDITIONS:
- {PLAN_RUN_FOLDER} created with base run files present
- Determine FEATURE_MODE upfront:
    new       = FEATURE_ID is reserved in REGISTRY.md (Planned (Reserved IDs)) but {FEATURE_PATH} does not exist
    existing  = {FEATURE_PATH} already exists with at least PRD.md and STATUS.md skeleton
- PHASE/FEATURE_MODE compatibility:
    PHASE=A, FEATURE_MODE=new       → plan creates {FEATURE_PATH} and scaffolds PRD/personas/stories/STATUS skeleton
    PHASE=A, FEATURE_MODE=existing  → plan updates the existing planning artifacts; STATUS.md story provenance rows are append-only (never mutated)
    PHASE=B, FEATURE_MODE=new       → REJECT: cannot run architecture before requirements exist; run PHASE=A or A+B instead
    PHASE=B, FEATURE_MODE=existing  → plan updates feature-assembly-plan.md and ontology bindings
    PHASE=A+B, FEATURE_MODE=new     → plan creates {FEATURE_PATH}, runs Phase A then Phase B
    PHASE=A+B, FEATURE_MODE=existing → plan updates planning artifacts then architecture
- `python3 {PRODUCT_ROOT}/scripts/kg/validate.py` exits 0 at start

CONTEXT LOADING ORDER:
1. agents/ROUTER.md
2. agents/agent-map.yaml
3. agents/docs/AGENT-USE.md
4. agents/actions/plan.md
5. {PRODUCT_ROOT}/planning-mds/features/REGISTRY.md (confirm FEATURE_ID is reserved or new)
6. {PRODUCT_ROOT}/planning-mds/BLUEPRINT.md (domain context)
7. {PRODUCT_ROOT}/planning-mds/knowledge-graph/solution-ontology.yaml (architectural context)

FORBIDDEN:
- Generating {PLAN_RUN_ID} with uuid4 or any non-contract format
- Writing or consuming `current-run.json` for any reason
- Producing role reports (g0-*, test-*, code-review-*, etc.) — those belong to the feature action's evidence package
- Creating a feature evidence package at {PRODUCT_ROOT}/planning-mds/operations/evidence/{FEATURE_ID}-{slug}/ during plan
- Skipping APPROVAL or ONTOLOGY SYNC gates
- Editing canonical-nodes.yaml or solution-ontology.yaml outside the Architect phase

OWNERSHIP:
- product-manager (Phase A) owns: PRD.md, persona files, acceptance criteria, story breakdown, initial STATUS.md skeleton
- architect (Phase B) owns: feature-assembly-plan.md, ADRs, API contract updates, schema updates, canonical-nodes.yaml updates, solution-ontology.yaml updates, feature-mappings.yaml additions

GATES:
- A0  PM REQUIREMENTS DRAFT — PRD, personas, acceptance criteria, story breakdown
- A1  PM APPROVAL GATE — user reviews requirements; PM records decision in gate-decisions.md
- B0  ARCHITECT ARCHITECTURE — feature-assembly-plan.md, ADRs, API/schema updates, ontology bindings
- B1  ONTOLOGY SYNC GATE — feature-mappings.yaml + canonical-nodes.yaml + solution-ontology.yaml aligned with the assembly plan; `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-drift` exit 0
- B2  ARCHITECT APPROVAL GATE — user reviews architecture; architect records decision in gate-decisions.md

EVIDENCE OUTPUTS (in {PLAN_RUN_FOLDER}):
- README.md (Run Summary, Status, Evidence Index, Validation Summary, Open Follow-ups)
- action-context.md (Run Identity, Inputs, Assumptions, Scope Boundaries, Lifecycle Stage = "Plan")
- artifact-trace.md (which planning files were created/updated; pointer to {FEATURE_PATH}/feature-assembly-plan.md and PRD.md)
- gate-decisions.md (one row per gate: A0, A1, B0, B1, B2)
- commands.log (JSONL per §13 schema)
- lifecycle-gates.log (validator results)

EVIDENCE OUTPUTS (in {FEATURE_PATH}):
- PRD.md (Phase A)
- persona files, acceptance-criteria-checklist.md (Phase A)
- story files under {FEATURE_PATH}/stories/ or per product convention (Phase A)
- STATUS.md skeleton with Required Role Matrix and empty Story Provenance table (Phase A)
- feature-assembly-plan.md (Phase B)
- ADRs under {FEATURE_PATH}/adrs/ as applicable (Phase B)
- README.md and GETTING-STARTED.md (Phase B)

STOP CONDITIONS:
- PRD approval refused by user
- Architecture approval refused by user
- Ontology sync gate fails and cannot be reconciled
- `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-drift` fails after one repair cycle
- Canonical node edit attempted outside Architect role

EXIT VALIDATION (run in order; all exit 0):
- `python3 agents/product-manager/scripts/validate-trackers.py` (with FEATURE_ID context if applicable)
- `python3 agents/product-manager/scripts/generate-story-index.py {PRODUCT_ROOT}/planning-mds/features/`
- `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-drift`
- `python3 agents/scripts/validate_templates.py`
- NOTE: do NOT call validate-feature-evidence.py at plan — there is no feature evidence package yet

CONFLICT RESOLUTION:
- PRD vs architecture conflict → resolve in Phase B before architecture approval; do not silently change PRD
- existing assembly plan vs new architecture → log reconciliation in gate-decisions.md; never silently overwrite
- ontology binding conflict → halt; resolve in canonical-nodes.yaml first
