Before starting, resolve `{PRODUCT_ROOT}` per `agents/docs/AGENT-USE.md` → Session Setup and echo its absolute path on your first turn. This prompt encodes the blog action under `feature-evidence-package-standardization-plan-v2.md` (effective `2026-05-19`). Blog produces development logs, technical articles, and channel amplification content. It is OUTSIDE the feature evidence contract — it does NOT produce role reports, is NOT evidence for any completed terminal feature, and is NOT required by any validator. It still produces a base run evidence package per §8 so the blog run is auditable.

Generate `{BLOG_RUN_ID}` once at session start using the contract format `YYYY-MM-DD-[a-z0-9]{8}` (suffix from `python3 -c "import secrets; print(secrets.token_hex(4))"`). Do not use `uuid4`.

Create `BLOG_RUN_FOLDER` at `{PRODUCT_ROOT}/planning-mds/operations/evidence/{BLOG_RUN_ID}/` and initialize the six §8 base run files from templates.

Run `agents/actions/blog.md` with `POST_TYPE={devlog | technical-article | release-post | retrospective | other}`, `TARGET_PATH={where the post will be written}`, `AMPLIFICATION={none | phase-2}` (whether to produce channel derivatives after the primary post), and optionally `FEATURE_REF={F####}` for context. `FEATURE_REF` does NOT make this a feature-scoped run — it is read-only context.

Load context in this order: `agents/ROUTER.md` → `agents/agent-map.yaml` → `agents/docs/AGENT-USE.md` → `agents/actions/blog.md` → `agents/blogger/SKILL.md`. For `FEATURE_REF`, also load that feature's `README.md`, `PRD.md`, `feature-assembly-plan.md`, and (if archived) its `pm-closeout.md` — all read-only.

Don't generate `{BLOG_RUN_ID}` with `uuid4`. Don't write into any feature evidence package (`{PRODUCT_ROOT}/planning-mds/operations/evidence/F####-*/`). Don't cite a blog post as evidence for a completed terminal feature. Don't draft before the EDITORIAL BRIEF gate. Don't publish or amplify before the EDITORIAL GATE. Don't misrepresent feature status, dates, or decisions — cross-check claims against `REGISTRY.md` and `pm-closeout.md` when `FEATURE_REF` is set.

Append every shell command to `{BLOG_RUN_FOLDER}/commands.log` per the §13 JSONL schema.

Ownership: the blogger (per `agents/blogger/SKILL.md`) owns the post; the user owns approval.

Follow these gates exactly (they mirror `agents/actions/blog.md`):
- `B0 DISCOVERY` — conversational; the agent asks, recommends, and aligns with the user
- `B1 EDITORIAL BRIEF` — user approves the brief before drafting
- `B2 DRAFT` — write the primary post into `TARGET_PATH`
- `B3 SELF-REVIEW GATE` — accuracy and quality check
- `B4 EDITORIAL GATE` — user reviews and approves
- `B5 AMPLIFICATION` (optional Phase 2, only when `AMPLIFICATION=phase-2`) — produce channel derivatives

Evidence outputs land in two places. In `{BLOG_RUN_FOLDER}`: the six §8 base run files; `README.md` `Evidence Index` points to `TARGET_PATH` and any amplification artifacts; `action-context.md` records `Scope Boundaries = "Editorial content; not feature evidence"`. In `TARGET_PATH` and amplification destinations: the post and its derivatives.

Stop immediately if the user refuses the EDITORIAL BRIEF, if self-review identifies factual errors that cannot be resolved against source artifacts, or if the user refuses the EDITORIAL GATE.

Close the run by confirming `gate-decisions.md` records `B0..B5` (or `B0..B4` when `AMPLIFICATION=none`). No validators are required — blog content is not gated by feature evidence validators.

Resolve conflicts like this:
- blog claim disagrees with `REGISTRY.md`/`STATUS.md`/`pm-closeout.md` → registry/closeout wins; fix the post
- blog claim disagrees with code → code wins; do not publish content that misleads
