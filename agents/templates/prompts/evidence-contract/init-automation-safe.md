ACTION: agents/actions/init.md
CONTRACT: feature-evidence-package-standardization-plan-v2.md (effective 2026-05-19)
CONTRACT SCOPE: Init bootstraps a new product. It runs BEFORE any feature exists, so there is no feature evidence package to produce. Init still produces a base run evidence package per §8 so the bootstrap itself is auditable.

SESSION_SETUP:
- Resolve {PRODUCT_ROOT} per agents/docs/AGENT-USE.md → Session Setup (operator input, NEBULA_PRODUCT_ROOT env var, or default `../<product-repo>`)
- Echo resolved absolute {PRODUCT_ROOT}
- Confirm {PRODUCT_ROOT} is empty or a new repository willing to accept scaffolded files
- Generate {INIT_RUN_ID} once at session start using contract format YYYY-MM-DD-[a-z0-9]{8} (suffix from `secrets.token_hex(4)`). DO NOT use uuid4.
- Create base run folder per §8 (created after {PRODUCT_ROOT} scaffolding lands operations/evidence/):
    INIT_RUN_FOLDER = {PRODUCT_ROOT}/planning-mds/operations/evidence/{INIT_RUN_ID}/
    mkdir -p {INIT_RUN_FOLDER}
- Initialize base run files: README.md, action-context.md, artifact-trace.md, gate-decisions.md, commands.log (empty JSONL), lifecycle-gates.log (empty)

PARAMETERS:
  PROJECT_NAME:        {string}
  DOMAIN_DESCRIPTION:  {1-2 sentence summary}
  TARGET_USERS:        [{role}, {role}, ...]
  CORE_ENTITIES:       [{entity}, {entity}, ...]
  INIT_RUN_ID:         {YYYY-MM-DD-[a-z0-9]{8}; generated per SESSION_SETUP}

PRECONDITIONS:
- nebula-agents is checked out and is the current session working directory
- {PRODUCT_ROOT} resolved and either empty or accepting scaffold
- Operator has basic project context (domain, goals, target users, initial entities)

CONTEXT LOADING ORDER:
1. agents/ROUTER.md
2. agents/agent-map.yaml
3. agents/docs/AGENT-USE.md
4. agents/actions/init.md
5. agents/product-manager/SKILL.md (initialization mode)
6. agents/templates/** (templates for scaffolded files)

FORBIDDEN:
- Generating {INIT_RUN_ID} with uuid4
- Scaffolding into a non-empty {PRODUCT_ROOT} without explicit operator confirmation
- Skipping the evidence directory bootstrap; the product must have `planning-mds/operations/evidence/` ready for first feature run
- Pre-populating REGISTRY.md with non-empty `Archived Features` or `Retired Features` tables; both start empty
- Setting Evidence Contract Effective Date earlier than the framework default (must be the framework default `2026-05-19` or later for new products)

REQUIRED TOOL INVOCATIONS:
- All shell commands appended to {INIT_RUN_FOLDER}/commands.log per §13 JSONL schema (once the folder exists)
- Final validator sweep at exit (see EXIT VALIDATION)

OWNERSHIP:
- product-manager (initialization mode) owns every scaffolded file

GATES:
- I0  PROJECT INPUTS CAPTURED — PROJECT_NAME, DOMAIN_DESCRIPTION, TARGET_USERS, CORE_ENTITIES recorded
- I1  PRODUCT_ROOT SCAFFOLD — create the canonical directory structure
- I2  BLUEPRINT TEMPLATE — produce {PRODUCT_ROOT}/planning-mds/BLUEPRINT.md from template
- I3  REGISTRY + ROADMAP — produce REGISTRY.md (empty Active/Planned/Archived/Retired sections), ROADMAP.md (empty Now/Next/Later/Completed)
- I4  EVIDENCE INFRASTRUCTURE — create planning-mds/operations/evidence/ with README explaining base run vs feature profile vs global lanes per §§7, 8, 9, 20; create the Path Class Extensions section (§7) empty by default. IF the product's intended top-level layout differs from the framework defaults (engine/, experience/) — for example a monorepo using apps/api/, apps/web/, or services/ — the operator MUST populate Path Class Extensions before the first feature action runs; init emits an info notice when BLUEPRINT.md mentions a non-default layout and the extensions section is still empty
- I5  KG INFRASTRUCTURE — create planning-mds/knowledge-graph/ with empty solution-ontology.yaml, canonical-nodes.yaml, feature-mappings.yaml, code-index.yaml
- I6  VALIDATOR SANITY — run all validators against the empty product; each must exit 0

EVIDENCE OUTPUTS (in {INIT_RUN_FOLDER}):
- README.md (Run Summary = "Product bootstrap", Status, Evidence Index, Validation Summary)
- action-context.md (Run Identity, Inputs, Assumptions, Scope Boundaries = "Bootstrap only", Lifecycle Stage = "Init")
- artifact-trace.md (every file scaffolded under {PRODUCT_ROOT})
- gate-decisions.md (I0..I6)
- commands.log
- lifecycle-gates.log

EVIDENCE OUTPUTS (in {PRODUCT_ROOT}/planning-mds/operations/evidence/README.md):
- Sections: "Base Run Profile" (§8), "Feature Evidence Profile" (§9), "Global Lanes" (§20)
- "Path Class Extensions" section (§7) — empty by default; the operator fills in any product-specific globs after I4

STOP CONDITIONS:
- Operator refuses to confirm scaffold into non-empty {PRODUCT_ROOT}
- Any validator exits non-zero at I6 (root cause must be fixed before init can complete)
- INSUFFICIENT_CONTEXT for any required input

EXIT VALIDATION (run in order; all exit 0):
- `python3 agents/product-manager/scripts/validate-trackers.py`
- `python3 agents/product-manager/scripts/validate-feature-evidence.py --product-root {PRODUCT_ROOT}` (registry-wide scan; should report 0 governed features and 0 retired records)
- `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-symbols`
- `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-drift`
- `python3 agents/scripts/validate_templates.py`

CONFLICT RESOLUTION:
- Operator wants effective date earlier than framework default → refuse; new products inherit the framework default at minimum
- Operator wants to backfill historical features during init → out of scope per §4 non-goals; init creates an empty registry only
