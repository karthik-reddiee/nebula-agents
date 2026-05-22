Before starting, resolve `{PRODUCT_ROOT}` per `agents/docs/AGENT-USE.md` → Session Setup and echo its absolute path on your first turn. This prompt encodes the test action under `feature-evidence-package-standardization-plan-v2.md` (effective `2026-05-19`). Test runs in two modes: feature-scoped (QE reports land in an existing feature run folder driven by `feature.md` G2) or standalone (QE reports land in a base run evidence folder, do NOT satisfy any feature evidence requirement).

Generate run IDs with the contract format `YYYY-MM-DD-[a-z0-9]{8}` (suffix from `python3 -c "import secrets; print(secrets.token_hex(4))"`). Do not use `uuid4`.

Decide MODE upfront:
- `feature-scoped` — pass `FEATURE_ID={F####}` and `RUN_ID={parent feature run ID}`. `OUTPUT_FOLDER` is `{PRODUCT_ROOT}/planning-mds/operations/evidence/{FEATURE_ID}-{slug}/{RUN_ID}/` and MUST already exist. Raw test results go under `{OUTPUT_FOLDER}/artifacts/test-results/`; raw coverage output under `{OUTPUT_FOLDER}/artifacts/coverage/`; visual regression snapshots (Playwright/Cypress/etc.) go under `{OUTPUT_FOLDER}/artifacts/screenshots/` when applicable. Do NOT create a new run folder.
- `standalone` — generate `{TEST_RUN_ID}` and create `TEST_RUN_FOLDER` at `{PRODUCT_ROOT}/planning-mds/operations/evidence/{TEST_RUN_ID}/` plus `artifacts/test-results/` and `artifacts/coverage/` subfolders. Initialize the six §8 base run files.

Run `agents/actions/test.md` with `MODE`, `TEST_SCOPE={unit | component | integration | e2e | api | accessibility | regression | all}`, and (for feature-scoped) `STORIES=[{F####-S####}, ...]`. Start only when the runtime containers are healthy and tests will execute inside them.

Load context in this order: `agents/ROUTER.md` → `agents/agent-map.yaml` → `agents/docs/AGENT-USE.md` → `agents/actions/test.md` → `agents/quality-engineer/SKILL.md`. For feature-scoped, also load `{FEATURE_PATH}/feature-assembly-plan.md`, `{FEATURE_PATH}/STATUS.md`, story files under the feature's local story breakdown, and `{OUTPUT_FOLDER}/evidence-manifest.json`.

Don't generate run IDs with `uuid4`. Don't write QE reports outside the chosen output folder. In feature-scoped mode, don't create a new `{FEATURE_ID}-{slug}` run folder. Don't skip `coverage-report.md` entirely — the file must exist even when coverage is waived (§10). Don't mock runtime layers in integration/E2E tests when raw runtime is available. Don't cite summary prose alone as evidence; artifact paths are required. Don't apply generic universal coverage thresholds — coverage targets are feature-scoped per §29.

All test commands run inside runtime containers and their artifact paths are recorded in `commands.log` per the §13 JSONL schema. Coverage tool output is stored under the `artifacts/coverage/` subfolder or, if it intentionally lives in an implementation-layer folder, referenced from `coverage-report.md` per §10.

Keep ownership strict: `quality-engineer` owns `test-plan.md`, `test-execution-report.md`, and `coverage-report.md`. The developer-vs-QE split for who writes which tests must be documented in `test-plan.md`.

For feature-scoped mode, write into `{OUTPUT_FOLDER}`:
- `test-plan.md` with the headings from §14 (story-to-AC mapping; unit/component/integration/E2E/API/accessibility strategy; developer-vs-QE test ownership; test data/fixtures; happy/edge/error/auth/accessibility/regression cases; `Result`)
- `test-execution-report.md` with the headings from §14 (commands executed; pass/fail counts; skipped tests and rationale; raw test artifact paths; failed/retried command history; AC coverage; `Result`)
- `coverage-report.md` (always exists) with the headings from §14 (coverage target and actual per layer; raw artifact paths; feature-scoped notes; waiver if coverage cannot be produced, with owner/date/scope/follow-up; `Result`)
- Raw test results copied or referenced under `{OUTPUT_FOLDER}/artifacts/test-results/`
- Raw coverage output copied or referenced under `{OUTPUT_FOLDER}/artifacts/coverage/`
- Visual regression snapshots copied or referenced under `{OUTPUT_FOLDER}/artifacts/screenshots/` when applicable (`screenshot_reference_missing_fails` when `test-execution-report.md` cites a screenshot path that does not resolve)
- Update `{OUTPUT_FOLDER}/evidence-manifest.json` `role_results.Quality Engineer` with `required_artifacts=[test-plan.md, test-execution-report.md, coverage-report.md]`, `verdict_artifact=test-execution-report.md`, and the current verdict
- If coverage is waived, populate `waivers.coverage` in the manifest with `required`, `reason`, `owner`, `approved_on`, `follow_up`

For standalone mode, write the same three reports plus the six §8 base run files into `{TEST_RUN_FOLDER}`. This run does NOT contribute to a feature evidence package.

Follow these gates exactly:
- `T0 TEST PLAN` — produce and review `test-plan.md`
- `T1 TEST EXECUTION` — produce `test-execution-report.md` with raw artifact paths
- `T2 COVERAGE` — produce `coverage-report.md` (with waiver inline if applicable)
- `T3 SELF-REVIEW GATE` — QE self-checks the three reports
- `T4 QUALITY GATE` — coverage and pass-rate thresholds met or waiver accepted
- `T5 STAGE VALIDATION` (feature-scoped only) — `python3 agents/product-manager/scripts/validate-feature-evidence.py --product-root {PRODUCT_ROOT} --feature {FEATURE_ID} --run-id {RUN_ID} --stage G2` exit 0

Stop immediately if `coverage-report.md` is missing (`missing_coverage_report_fails`), if `test-execution-report.md` is missing (`missing_test_execution_fails`), if `test-plan.md` is missing (`missing_test_plan_fails`), or if `INSUFFICIENT_CONTEXT` occurs. A coverage waiver that lacks PM acceptance is caught later at G4.7 (`coverage_waiver_missing_pm_acceptance_fails`).

Close the run:
- For feature-scoped: `validate-feature-evidence.py --feature {FEATURE_ID} --run-id {RUN_ID} --stage G2` exit 0
- For standalone: confirm the six base run files are complete; no feature-stage validation applies

Resolve conflicts like this:
- coverage target met but a story has no test → fail; add a test or document the AC exception
- coverage report exists but raw artifacts missing → fail (`coverage_claim_without_artifact_fails`)
- `test-execution-report.md` cites an artifact path that does not resolve → fail (`test_results_reference_missing_fails`)
- coverage waiver missing PM acceptance at closeout → resolved by G4.7
