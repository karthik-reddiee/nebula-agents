Before starting, resolve `{PRODUCT_ROOT}` per `agents/docs/AGENT-USE.md` → Session Setup and echo its absolute path on your first turn. This prompt encodes the review action under `feature-evidence-package-standardization-plan-v2.md` (effective `2026-05-19`). Review runs in two modes: feature-scoped (review reports land in an existing feature run folder driven by `feature.md` G3) or standalone (review reports land in a base run evidence folder, do NOT satisfy any feature evidence requirement).

Generate any run IDs with the contract format `YYYY-MM-DD-[a-z0-9]{8}` (suffix from `python3 -c "import secrets; print(secrets.token_hex(4))"`). Do not use `uuid4`. Do not regenerate after session start.

Decide MODE upfront:
- `feature-scoped` — pass `FEATURE_ID={F####}` and `RUN_ID={parent feature run ID}`. `OUTPUT_FOLDER` is `{PRODUCT_ROOT}/planning-mds/operations/evidence/{FEATURE_ID}-{slug}/{RUN_ID}/` and MUST already exist (created by `feature.md` at G0). Do NOT create a new run folder.
- `standalone` — generate `{REVIEW_RUN_ID}` and create `REVIEW_RUN_FOLDER` at `{PRODUCT_ROOT}/planning-mds/operations/evidence/{REVIEW_RUN_ID}/`. Initialize base run files (`README.md`, `action-context.md`, `artifact-trace.md`, `gate-decisions.md`, `commands.log`, `lifecycle-gates.log`) per §8.

Run `agents/actions/review.md` with `MODE`, `SCOPE={feature | path-set | codebase}`, and `PATHS=[...]` for path-set scope. For feature-scoped, the feature run folder must exist and G0 must have passed; for standalone, just initialize the base run folder.

Load context in this order: `agents/ROUTER.md` → `agents/agent-map.yaml` → `agents/docs/AGENT-USE.md` → `agents/actions/review.md`; for feature-scoped, also load `{FEATURE_PATH}/feature-assembly-plan.md`, `{FEATURE_PATH}/STATUS.md`, and `{OUTPUT_FOLDER}/evidence-manifest.json`. Load `agents/code-reviewer/SKILL.md` and (when security is in scope) `agents/security/SKILL.md`.

Don't generate run IDs with `uuid4`. Don't write role reports outside the chosen output folder. In feature-scoped mode, don't create a new `{FEATURE_ID}-{slug}` run folder during review — use the existing one. Don't mix feature-scoped and standalone outputs in one session. Don't skip security review when the feature manifest carries `security_sensitive_scope=true` (rule `security_required_missing_report_fails`).

Append every shell command to `commands.log` per the §13 JSONL schema. Compile/test/lint commands run inside runtime containers and their artifact paths are recorded in `commands.log`.

Keep ownership strict:
- `code-reviewer` owns `code-review-report.md`. Passing verdicts per §11 are `APPROVED`, `APPROVED WITH RECOMMENDATIONS`, `PASS`, or `PASS WITH RECOMMENDATIONS` — choose the `APPROVED` family for change-set review and the `PASS` family for codebase audits per `code-reviewer/SKILL.md`. Blocking verdicts are `REQUEST CHANGES` or `REJECTED`.
- `security-reviewer` owns `security-review-report.md` (Result: `PASS | PASS WITH RECOMMENDATIONS | FAIL`), only when scope includes security or the feature carries `security_sensitive_scope=true`

For feature-scoped mode, write into `{OUTPUT_FOLDER}`:
- `code-review-report.md` with the headings from §14 (reviewed files, validation artifacts, severity-ranked findings, recommendations with owner/follow-up, vertical-slice completeness, AC/test adequacy, architecture compliance, coverage verification, `Result`)
- `security-review-report.md` when required (headings per §14: reviewed surfaces, threat boundary, auth/authz, validation, audit/logging, secrets/config, OWASP Top 10 coverage, findings, recommendation disposition, `Result`)
- Update `{OUTPUT_FOLDER}/evidence-manifest.json` `role_results` for Code Reviewer (and Security Reviewer when applicable)
- Append commands and validator results to the feature run folder's `commands.log` and `lifecycle-gates.log`

For standalone mode, write the same role reports plus the six §8 base run files into `{REVIEW_RUN_FOLDER}`. This run does NOT contribute to a feature evidence package and does NOT satisfy the per-feature review requirement — the corresponding `feature.md` run must still produce its own G3 evidence.

Follow these gates exactly:
- `R0 REVIEW SCOPE LOCK` — confirm `SCOPE` and `PATHS`; record in `gate-decisions.md` (or `action-context.md` for standalone)
- `R1 PARALLEL REVIEWS` — code review and (when applicable) security review run in parallel
- `R2 APPROVAL GATE` — user reviews findings; reviewers record verdicts
- `R3 STAGE VALIDATION` (feature-scoped only) — `python3 agents/product-manager/scripts/validate-feature-evidence.py --product-root {PRODUCT_ROOT} --feature {FEATURE_ID} --run-id {RUN_ID} --stage G3` exit 0

Stop immediately if a critical code or security finding persists after one review cycle and the parent feature action expects this review to pass, if required security review is skipped when `security_sensitive_scope=true`, or if `INSUFFICIENT_CONTEXT` occurs.

Close the run:
- For feature-scoped: `validate-feature-evidence.py --feature {FEATURE_ID} --run-id {RUN_ID} --stage G3` exit 0
- For standalone: confirm the six base run files are complete; no feature-stage validation applies

Resolve conflicts like this:
- code review APPROVED but security review FAIL → blocking; resolve in same change set or escalate
- review reports disagree with manifest `role_results` → fix the manifest at G4.5; reports are authoritative
- review attempted on a feature whose G2 has not yet passed → halt; out of sequence
