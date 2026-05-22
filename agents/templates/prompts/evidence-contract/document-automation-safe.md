ACTION: agents/actions/document.md
CONTRACT: feature-evidence-package-standardization-plan-v2.md (effective 2026-05-19)
CONTRACT SCOPE: Document produces technical documentation (API docs, READMEs, runbooks, developer guides). It is OUTSIDE the feature evidence contract — it does NOT produce role reports for any feature evidence package and does NOT need to be cited as evidence for a completed terminal feature. It still produces a base run evidence package per §8 so the documentation run is auditable.

SESSION_SETUP:
- Resolve {PRODUCT_ROOT} per agents/docs/AGENT-USE.md → Session Setup
- Echo resolved absolute {PRODUCT_ROOT}
- Generate {DOC_RUN_ID} once at session start using contract format YYYY-MM-DD-[a-z0-9]{8} (suffix from `secrets.token_hex(4)`). DO NOT use uuid4.
- Create base run folder per §8:
    DOC_RUN_FOLDER = {PRODUCT_ROOT}/planning-mds/operations/evidence/{DOC_RUN_ID}/
    mkdir -p {DOC_RUN_FOLDER}
- Initialize base run files from templates: README.md, action-context.md, artifact-trace.md, gate-decisions.md, commands.log, lifecycle-gates.log

PARAMETERS:
  DOC_RUN_ID:     {YYYY-MM-DD-[a-z0-9]{8}; generated per SESSION_SETUP}
  DOC_SCOPE:      {api | readme | runbook | developer-guide | release-notes | mixed}
  TARGETS:        [{path}, {path}, ...]                            # destination doc files
  SOURCE_CODE:    [{path}, {path}, ...]                            # source code basis for the docs (optional)
  FEATURE_REF:    {F####}                                          # optional reference for context; does NOT make this a feature-scoped run

PRECONDITIONS:
- {DOC_RUN_FOLDER} created with base run files
- For api/runbook docs: application runtime containers healthy for verification

CONTEXT LOADING ORDER:
1. agents/ROUTER.md
2. agents/agent-map.yaml
3. agents/docs/AGENT-USE.md
4. agents/actions/document.md
5. agents/technical-writer/SKILL.md
6. SOURCE_CODE paths (read-only)
7. For FEATURE_REF: {FEATURE_PATH}/README.md, PRD.md, feature-assembly-plan.md (read-only context)

FORBIDDEN:
- Generating {DOC_RUN_ID} with uuid4
- Writing into any feature evidence package (`{PRODUCT_ROOT}/planning-mds/operations/evidence/F####-*/`)
- Citing documentation as a substitute for required feature evidence reports (e.g. test-execution-report.md, code-review-report.md)
- Executing compile/lint/runtime commands outside runtime containers
- Skipping the SELF-REVIEW or APPROVAL gates from agents/actions/document.md

REQUIRED TOOL INVOCATIONS:
- All shell commands appended to {DOC_RUN_FOLDER}/commands.log per §13 JSONL schema
- Runtime verifications (API examples, CLI commands, health checks) run in runtime containers when feasible; record artifact paths

OWNERSHIP:
- technical-writer (per agents/technical-writer/SKILL.md) owns every produced doc file

GATES:
- D0  SCOPE LOCK — confirm DOC_SCOPE, TARGETS, SOURCE_CODE; record in gate-decisions.md
- D1  DRAFT — produce or update the TARGETS
- D2  SELF-REVIEW GATE — author validates documentation quality and accuracy (per agents/actions/document.md)
- D3  APPROVAL GATE — user reviews documentation

EVIDENCE OUTPUTS (in {DOC_RUN_FOLDER}):
- README.md (Run Summary = "Documentation run", Status, Evidence Index pointing to TARGETS, Validation Summary, Open Follow-ups)
- action-context.md (Run Identity, Inputs = DOC_SCOPE/TARGETS/SOURCE_CODE/optional FEATURE_REF, Assumptions, Scope Boundaries = "Documentation only; not feature evidence", Lifecycle Stage = "Document")
- artifact-trace.md (which TARGETS were created/updated; pointers to SOURCE_CODE)
- gate-decisions.md (D0..D3)
- commands.log (any runtime verification commands)
- lifecycle-gates.log (validator results from EXIT VALIDATION)

EVIDENCE OUTPUTS (in TARGETS): the documentation files themselves; format and headings depend on the doc type

STOP CONDITIONS:
- Self-review identifies factual errors that cannot be resolved against source code
- Runtime verification fails and the doc would mislead users
- Approval refused by user

EXIT VALIDATION:
- `python3 agents/scripts/validate_templates.py` exit 0
- `python3 {PRODUCT_ROOT}/scripts/kg/validate.py --check-drift` exit 0 (only required when KG references changed)
- DO NOT call validate-feature-evidence.py — there is no feature evidence package for this run

CONFLICT RESOLUTION:
- doc disagrees with code → code wins; update the doc, not the code
- doc disagrees with API contract → contract wins; route to plan or architect if the contract itself is wrong
- doc cites a runtime example that does not work → fix or remove the example; do not ship docs that mislead
