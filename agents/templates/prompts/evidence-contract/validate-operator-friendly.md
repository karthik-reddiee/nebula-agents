Before starting, resolve `{PRODUCT_ROOT}` per `agents/docs/AGENT-USE.md` → Session Setup and echo its absolute path on your first turn. This prompt encodes the validate action under `feature-evidence-package-standardization-plan-v2.md` (effective `2026-05-19`). Validate is a parallel-agent validation action: Product Manager reviews requirements, Architect reviews architecture, and (when scope includes implementation) either agent invokes the framework validators (`validate-feature-evidence.py`, `validate-trackers.py`, `kg/validate.py`, `generate-story-index.py`, `validate_templates.py`) as tools. It produces a base run evidence package per §8 with per-agent validation reports; it does NOT write into any feature evidence package.

Generate `{VALIDATE_RUN_ID}` once at session start using the contract format `YYYY-MM-DD-[a-z0-9]{8}` (suffix from `python3 -c "import secrets; print(secrets.token_hex(4))"`). Do not use `uuid4`.

Create `VALIDATE_RUN_FOLDER` at `{PRODUCT_ROOT}/planning-mds/operations/evidence/{VALIDATE_RUN_ID}/` and initialize the six §8 base run files from templates. Create the `artifacts/` subfolder for JSON output capture.

Run `agents/actions/validate.md` with `VALIDATION_SCOPE={requirements | architecture | implementation | all}` and (when implementation validation targets a specific feature) `FEATURE_ID={F####}`, optional `RUN_ID={parent feature run ID}` (required for stages G0..G4.5), and `STAGE` defaulting to `closeout`. `EFFECTIVE_DATE` defaults to `2026-05-19` and is rejected if earlier than the framework default (`effective_date_override_earlier_than_default_fails`).

Load context in this order: `agents/ROUTER.md` → `agents/agent-map.yaml` → `agents/docs/AGENT-USE.md` → `agents/actions/validate.md` → `agents/product-manager/SKILL.md` (requirements validation mode) → `agents/architect/SKILL.md` (architecture validation mode). When implementation is in scope, also load `agents/product-manager/scripts/README.md` for validator commands and exit codes.

Don't generate `{VALIDATE_RUN_ID}` with `uuid4`. Don't write into any feature evidence package (validate is read-only with respect to feature packages). Don't treat validator script output as a substitute for the PM/Architect agent-level validation work. Don't pass `--evidence-effective-date` earlier than the framework default. Don't call `--stage G4.7` or `--stage closeout` when invoked transitively from `validate-trackers.py` context (§17 step 2 forbids this). Don't produce summaries that downgrade errors to warnings. Don't skip the SELF-REVIEW gate per agent. Don't bypass the APPROVAL gate before reporting results upstream.

Keep ownership strict:
- Product Manager (requirements validation) owns `{VALIDATE_RUN_FOLDER}/pm-validation-report.md`
- Architect (architecture validation) owns `{VALIDATE_RUN_FOLDER}/architect-validation-report.md`
- Implementation validation (run by either or both based on scope) owns `{VALIDATE_RUN_FOLDER}/implementation-validation-report.md`

Follow these gates exactly:

- `V0 SCOPE LOCK` — record `VALIDATION_SCOPE`, `FEATURE_ID`, `STAGE` in `action-context.md`; decide which agent(s) run in parallel based on scope
- `V1 PARALLEL VALIDATION (PM + Architect)`:
  - **1a. Product Manager (Requirements Validation)** — when scope includes `requirements` or `all`. Execute the requirements completeness, vision/non-goals, persona, feature traceability, story testability, and acceptance criteria checks listed in `agents/actions/validate.md` Step 1a. Produce `pm-validation-report.md` with sections: Completeness, Vision & Non-Goals, Personas, Feature Traceability, Story Testability, Acceptance Criteria, Findings (severity-ranked), `Result`
  - **1b. Architect (Architecture Validation)** — when scope includes `architecture` or `all`. Execute the solution-ontology, canonical-nodes, feature-mappings, API contract, schema, authorization, and assembly-plan consistency checks listed in `validate.md` Step 1b. Produce `architect-validation-report.md` with sections: Ontology Integrity, Canonical Nodes, Feature Mappings, API Contracts, Schemas, Authorization, Assembly-Plan Alignment, Findings (severity-ranked), `Result`
  - **1c. Implementation Validation (script-driven)** — when scope includes `implementation` or `all`. Owner is PM unless `FEATURE_ID` narrows to a feature in active development, in which case the feature's orchestrator/PM. Run the validator scripts and capture results. Append every command to `commands.log` per the §13 JSONL schema.
    - For `FEATURE_ID` unset (registry-wide), run in order: `validate-trackers.py` → `validate-feature-evidence.py --product-root {PRODUCT_ROOT} --json` (capture to `artifacts/feature-evidence-validation.json`) → `generate-story-index.py` → `kg/validate.py --check-symbols` → `kg/validate.py --check-drift` → `validate_templates.py`.
    - For `FEATURE_ID` set, run: `validate-feature-evidence.py --feature {FEATURE_ID} [--run-id {RUN_ID}] --stage {STAGE} --json` (capture to `artifacts/feature-evidence-validation.json`) → `validate-trackers.py --feature {FEATURE_ID} [--run-id {RUN_ID}]` → `kg/validate.py --check-drift` → `validate_templates.py`.
    - Produce `implementation-validation-report.md` with: commands executed, exit codes, errors/warnings/info from validator output (cite rule IDs per §22), KG drift status, template alignment status, Findings, `Result`
- `V2 SELF-REVIEW GATE` — each producing agent reviews its own report for completeness and accuracy
- `V3 APPROVAL GATE` — user reviews all produced reports and decides next steps; record the decision in `gate-decisions.md`

Evidence outputs land in `{VALIDATE_RUN_FOLDER}`: the six §8 base run files; `pm-validation-report.md` (when in scope); `architect-validation-report.md` (when in scope); `implementation-validation-report.md` (when in scope); `artifacts/feature-evidence-validation.json` (when implementation validation ran); `README.md` Validation Summary aggregates per-agent verdicts and per-validator results.

Stop immediately if any validator returns exit code 2 (escalate to user), if any error-severity rule fires on a governed completed terminal feature and the operator does not authorize the validator-defect waiver path, if KG drift is detected and not auto-repairable, if an effective-date override is attempted with an earlier-than-default value, if two approved manifests are detected for the same feature (escalate to PM), if either agent's SELF-REVIEW finds its own report materially incomplete, or if the user refuses the APPROVAL GATE.

Close the run when all scope-applicable commands exit 0 (or exit 2 has been escalated), all required per-agent reports are present and reviewed at V2, `README.md` Validation Summary is populated, and `gate-decisions.md` records V0 through V3.

Resolve conflicts like this:
- PM findings disagree with Architect findings on the same artifact → escalate to user at V3; do not silently reconcile
- `validate-trackers.py` reports a rule that `validate-feature-evidence.py` owns → defer to the feature evidence validator (single source of truth per §22)
- `validate-feature-evidence.py` reports an error you believe is a validator defect → do NOT bypass via `--evidence-effective-date`; route to the Phase 5 validator-defect fallback (record `waivers.validator_defect` in the affected feature manifest with follow-up; for in-progress features, log the defect as a mid-stage follow-up and create the waiver entry only when that feature reaches G4.7)
- registry-wide scan reports a pre-contract archived feature requiring evidence → check the `Evidence Reentry Date` on that archived row; absence means no reentry is claimed, so the requirement is the bug
