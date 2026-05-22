ACTION: agents/actions/blog.md
CONTRACT: feature-evidence-package-standardization-plan-v2.md (effective 2026-05-19)
CONTRACT SCOPE: Blog produces development logs, technical articles, and channel amplification content. It is OUTSIDE the feature evidence contract — it does NOT produce role reports, is NOT evidence for any completed terminal feature, and is NOT required by any validator. It still produces a base run evidence package per §8 so the blog run is auditable.

SESSION_SETUP:
- Resolve {PRODUCT_ROOT} per agents/docs/AGENT-USE.md → Session Setup
- Echo resolved absolute {PRODUCT_ROOT}
- Generate {BLOG_RUN_ID} once at session start using contract format YYYY-MM-DD-[a-z0-9]{8} (suffix from `secrets.token_hex(4)`). DO NOT use uuid4.
- Create base run folder per §8:
    BLOG_RUN_FOLDER = {PRODUCT_ROOT}/planning-mds/operations/evidence/{BLOG_RUN_ID}/
    mkdir -p {BLOG_RUN_FOLDER}
- Initialize base run files from templates: README.md, action-context.md, artifact-trace.md, gate-decisions.md, commands.log, lifecycle-gates.log

PARAMETERS:
  BLOG_RUN_ID:    {YYYY-MM-DD-[a-z0-9]{8}; generated per SESSION_SETUP}
  POST_TYPE:      {devlog | technical-article | release-post | retrospective | other}
  TARGET_PATH:    {path to where the post will be written}
  AMPLIFICATION:  {none | phase-2}                                 # whether to produce channel derivatives after the primary post
  FEATURE_REF:    {F####}                                          # optional reference for context

PRECONDITIONS:
- {BLOG_RUN_FOLDER} created with base run files
- Operator has subject context (what to write about)
- For FEATURE_REF: that feature exists in REGISTRY.md (Active, Archived, or Retired)

CONTEXT LOADING ORDER:
1. agents/ROUTER.md
2. agents/agent-map.yaml
3. agents/docs/AGENT-USE.md
4. agents/actions/blog.md
5. agents/blogger/SKILL.md
6. For FEATURE_REF (read-only context): {FEATURE_PATH}/README.md, PRD.md, feature-assembly-plan.md, and if archived, that feature's pm-closeout.md

FORBIDDEN:
- Generating {BLOG_RUN_ID} with uuid4
- Writing into any feature evidence package (`{PRODUCT_ROOT}/planning-mds/operations/evidence/F####-*/`)
- Citing a blog post as evidence for a completed terminal feature
- Drafting before the EDITORIAL BRIEF gate per agents/actions/blog.md
- Publishing or amplifying before the EDITORIAL GATE per agents/actions/blog.md
- Misrepresenting feature status, dates, or decisions (cross-check against REGISTRY.md and pm-closeout.md when FEATURE_REF is set)

REQUIRED TOOL INVOCATIONS:
- All shell commands appended to {BLOG_RUN_FOLDER}/commands.log per §13 JSONL schema

OWNERSHIP:
- blogger (per agents/blogger/SKILL.md) owns the post; user owns approval

GATES (mirror agents/actions/blog.md):
- B0  DISCOVERY — conversational; agent asks, recommends, aligns with user
- B1  EDITORIAL BRIEF — user approves brief before drafting
- B2  DRAFT — write primary post into TARGET_PATH
- B3  SELF-REVIEW GATE — accuracy and quality check
- B4  EDITORIAL GATE — user reviews and approves
- B5  AMPLIFICATION (optional Phase 2 if AMPLIFICATION=phase-2) — channel derivatives produced

EVIDENCE OUTPUTS (in {BLOG_RUN_FOLDER}):
- README.md (Run Summary = "Blog run", Status, Evidence Index pointing to TARGET_PATH and any amplification artifacts, Validation Summary, Open Follow-ups)
- action-context.md (Run Identity, Inputs = POST_TYPE/TARGET_PATH/optional FEATURE_REF, Assumptions, Scope Boundaries = "Editorial content; not feature evidence", Lifecycle Stage = "Blog")
- artifact-trace.md (TARGET_PATH and any channel derivative paths)
- gate-decisions.md (B0..B5)
- commands.log

EVIDENCE OUTPUTS (in TARGET_PATH and amplification destinations): the blog post and its derivatives

STOP CONDITIONS:
- User refuses the EDITORIAL BRIEF
- Self-review identifies factual errors that cannot be resolved against source artifacts
- User refuses the EDITORIAL GATE

EXIT VALIDATION:
- No validators required; blog content is not gated by feature evidence validators
- Confirm gate-decisions.md records all B0..B5 (or B0..B4 if AMPLIFICATION=none)

CONFLICT RESOLUTION:
- blog claim disagrees with REGISTRY.md/STATUS.md/pm-closeout.md → registry/closeout wins; fix the post
- blog claim disagrees with code → code wins; do not publish content that misleads
