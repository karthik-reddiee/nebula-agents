Before starting, resolve `{PRODUCT_ROOT}` per `agents/docs/AGENT-USE.md` → Session Setup (operator input, `NEBULA_PRODUCT_ROOT` env var, or default `../<product-repo>`) and echo its absolute path on your first turn. This prompt encodes the init action under `feature-evidence-package-standardization-plan-v2.md` (effective `2026-05-19`). Init bootstraps a brand-new product — there are no features yet, so no feature evidence package exists. Init still produces a base run evidence package per §8 so the bootstrap itself is auditable.

Confirm `{PRODUCT_ROOT}` is empty or a new repository willing to accept scaffolded files. If it's non-empty, do not proceed without explicit operator confirmation.

Generate `{INIT_RUN_ID}` once at session start using the contract format `YYYY-MM-DD-[a-z0-9]{8}` (suffix from `python3 -c "import secrets; print(secrets.token_hex(4))"`). Do not use `uuid4`.

Create `INIT_RUN_FOLDER` at `{PRODUCT_ROOT}/planning-mds/operations/evidence/{INIT_RUN_ID}/` (created once `operations/evidence/` has been scaffolded by gate I4). Initialize the six §8 base run files from templates.

Run `agents/actions/init.md` with `PROJECT_NAME`, `DOMAIN_DESCRIPTION` (1-2 sentences), `TARGET_USERS` (list of roles), and `CORE_ENTITIES` (initial baseline list). Start only when `nebula-agents` is checked out, `{PRODUCT_ROOT}` is resolved and accepting scaffold, and the operator has basic project context.

Load context in this order: `agents/ROUTER.md` → `agents/agent-map.yaml` → `agents/docs/AGENT-USE.md` → `agents/actions/init.md` → `agents/product-manager/SKILL.md` (initialization mode) → `agents/templates/**` for scaffolded file templates.

Don't generate `{INIT_RUN_ID}` with `uuid4`. Don't scaffold into a non-empty `{PRODUCT_ROOT}` without operator confirmation. Don't skip the evidence directory bootstrap — the product must have `planning-mds/operations/evidence/` ready before the first feature run. Don't pre-populate `REGISTRY.md` with non-empty `Archived Features` or `Retired Features` tables; both start empty. Don't set the Evidence Contract Effective Date earlier than the framework default — new products inherit `2026-05-19` at minimum.

Append every shell command (once `commands.log` exists) to `{INIT_RUN_FOLDER}/commands.log` per the §13 JSONL schema.

Keep ownership simple: `product-manager` (initialization mode) owns every scaffolded file.

Follow these gates exactly:
- `I0 PROJECT INPUTS CAPTURED` — record `PROJECT_NAME`, `DOMAIN_DESCRIPTION`, `TARGET_USERS`, `CORE_ENTITIES`
- `I1 PRODUCT_ROOT SCAFFOLD` — create the canonical directory structure under `{PRODUCT_ROOT}`
- `I2 BLUEPRINT TEMPLATE` — produce `{PRODUCT_ROOT}/planning-mds/BLUEPRINT.md` from the template
- `I3 REGISTRY + ROADMAP` — produce `REGISTRY.md` (empty Active/Planned/Archived/Retired) and `ROADMAP.md` (empty Now/Next/Later/Completed)
- `I4 EVIDENCE INFRASTRUCTURE` — create `planning-mds/operations/evidence/` with a README explaining Base Run Profile (§8), Feature Evidence Profile (§9), Global Lanes (§20), and an empty `Path Class Extensions` section (§7). If the product's intended top-level layout differs from the framework defaults (`engine/`, `experience/`) — e.g. a monorepo using `apps/api/`, `apps/web/`, or `services/` — the operator MUST populate `Path Class Extensions` before the first feature action runs. Init emits an info notice when `BLUEPRINT.md` mentions a non-default layout and the extensions section is still empty.
- `I5 KG INFRASTRUCTURE` — create `planning-mds/knowledge-graph/` with empty `solution-ontology.yaml`, `canonical-nodes.yaml`, `feature-mappings.yaml`, `code-index.yaml`
- `I6 VALIDATOR SANITY` — run all validators against the empty product; each must exit 0

Evidence outputs land in two places. In `{INIT_RUN_FOLDER}`: the six §8 base run files plus `gate-decisions.md` rows for `I0..I6` and an `Evidence Index` in `README.md` pointing to the scaffolded files. In `{PRODUCT_ROOT}/planning-mds/operations/evidence/README.md`: sections describing Base Run Profile, Feature Evidence Profile, Global Lanes, and an empty `Path Class Extensions` section.

Stop immediately if the operator refuses to confirm scaffolding into a non-empty `{PRODUCT_ROOT}`, if any validator exits non-zero at I6 (root cause must be fixed before init can complete), or if `INSUFFICIENT_CONTEXT` occurs for any required input.

Close the run by executing these in order, each exit 0:
- `python3 agents/product-manager/scripts/validate-trackers.py`
- `python3 agents/product-manager/scripts/validate-feature-evidence.py --product-root {PRODUCT_ROOT}` (registry-wide scan; should report zero governed features and zero retired records)
- `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-symbols`
- `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-drift`
- `python3 agents/scripts/validate_templates.py`

Resolve conflicts like this:
- operator wants an effective date earlier than the framework default → refuse; new products inherit the framework default at minimum
- operator wants to backfill historical features during init → out of scope per §4 non-goals; init creates an empty registry only
