# Token Comparison Report for F0019

Date: 2026-06-09  
Target product repo: `nebula-insurance-crm`  
Report location: `nebula-agents/compare-token-usage-for-F0019.md`

## Executive Summary

The F0019 work in `nebula-insurance-crm` was implemented after applying the same token-optimization approach used in `nebula-agents`: context was narrowed by feature, broad planning/source folders were kept out of default prompts, examples and archives were made on-demand, and exact files were loaded only when needed.

Estimated token consumption dropped from about **1,733,028 tokens** in the old broad-loading model to:

| Scenario | Estimated tokens | Reduction | Reduction % |
|---|---:|---:|---:|
| Before optimization: broad planning + broad source context | 1,733,028 | - | - |
| After optimization: default F0019 context + exact changed code files | 85,955 | 1,647,073 | 95.0% |
| After optimization: default F0019 context + KG index files + exact changed code files | 109,819 | 1,623,209 | 93.7% |

The practical reduction range for F0019 is therefore **about 93.7% to 95.0%**, depending on whether the larger knowledge-graph index files are counted as loaded context or treated as tool-query/index lookup output.

## Measurement Method

Exact LLM telemetry was not available from the local implementation run, so this report uses deterministic local file-size estimates.

Estimation rules:

| Content type | Rule used |
|---|---|
| Markdown/YAML/JSON planning prompt files | `1 word ~= 1.3 tokens`, matching `planning-mds/context-map.yaml` |
| Source code files | `1 token ~= 4 characters`, a conservative code-token approximation |
| Excluded generated folders | `node_modules`, `bin`, `obj`, coverage, test results, Vite output |

The numbers are estimates, but the comparison is apples-to-apples: before and after were calculated from the same local repo state and same counting script.

## Before Optimization

Before the token optimization, an agent implementation run could reasonably pull broad project context:

| Before context area | Files | Estimated tokens | Why it was expensive |
|---|---:|---:|---|
| Broad `planning-mds` planning/docs context | 623 | 847,544 | Included active features, archived features, examples, evidence, API/schema docs, and broad product docs |
| Broad `engine` + `experience` + `neuron` source context | 658 | 885,484 | Included full backend, frontend, AI layer, tests, mocks, and unrelated modules |
| **Total before** | **1,281** | **1,733,028** | Broad loading mixed product memory, examples, archive, source, and tests by default |

This broad-loading style was especially costly for F0019 because the repo contains many planning surfaces unrelated to submission quoting:

| Large context now avoided by default | Files | Estimated tokens avoided |
|---|---:|---:|
| Archived feature docs | 256 | 373,279 |
| Operations/evidence docs | 131 | 78,220 |
| Examples docs | 8 | 22,790 |
| API/schema/LOB-schema docs | 90 | 41,878 |
| All active feature docs instead of only F0019 | 63 | 32,657 |

## After Optimization

After optimization, the working set is routed by `planning-mds/context-map.yaml`.

Default prompt layers:

| Layer | Loaded by default? | Purpose |
|---|---|---|
| `product_core` | Yes | Minimal product entry points: README, lifecycle stage, feature registry, roadmap, `.agentignore` |
| `feature_scope` | Yes | Only the target feature folder, here F0019 |
| `knowledge_graph_scope` | Yes, as lookup/hint output | Compressed routing before loading raw artifacts |
| `architecture_scope` | No | Exact file only when feature or validation points to it |
| `api_schema_scope` | No | Exact endpoints/schemas only when touched |
| `frontend_scope` | No | Exact changed/hinted frontend files only |
| `backend_scope` | No | Exact changed/hinted backend files only |
| `evidence_scope` | No | Only explicit audit/validation evidence |
| `archive_scope` | No | Only explicit provenance/regression review |
| `examples` | No | Only when examples are requested or artifact shape is unclear |

After context loaded for F0019:

| After context area | Files | Estimated tokens |
|---|---:|---:|
| Product core + exact F0019 planning docs | 11 | 7,761 |
| Product core + exact F0019 docs + KG index files | 14 | 31,625 |
| Exact F0019 code/test files touched or inspected | 23 | 78,194 |

Combined after totals:

| After bundle | Estimated tokens |
|---|---:|
| Default prompt + exact code files | 85,955 |
| Default prompt + KG files + exact code files | 109,819 |

## Where Token Consumption Was Reduced

### 1. Broad `planning-mds/**` Loading Was Replaced

Before:

- The agent could load most or all planning docs.
- This included product blueprint, feature registry, active features, archived features, example docs, validation records, operations evidence, API specs, and schema docs.
- Estimated planning prompt load: **847,544 tokens**.

After:

- `planning-mds/context-map.yaml` limits default planning context to product core plus the target feature.
- F0019 planning context became only product entry points plus:
  - `planning-mds/features/F0019-submission-quoting-proposal-and-approval/GETTING-STARTED.md`
  - `PRD.md`
  - `README.md`
  - `STATUS.md`
  - `feature-assembly-plan.md`
  - `feature_update.md`
- Estimated optimized planning prompt load: **7,761 tokens** without KG files.

Reduction:

- Planning/doc context reduced by about **839,783 tokens**.
- Planning/doc reduction: about **99.1%**.

### 2. Archive Docs Were Removed From Default Context

Before:

- Historical features under `planning-mds/features/archive/**` could be loaded even when the active work was F0019.
- Estimated archive docs: **373,279 tokens**.

After:

- `.agentignore` marks archived feature folders as historical context.
- Archive files are loaded only for provenance, regression comparison, or explicit user request.
- For F0019 implementation, archive docs were not needed by default.

Reduction:

- Avoided about **373K tokens** from archive docs alone.

### 3. Operations Evidence Was Made Cold Storage

Before:

- Evidence and run logs could enter prompt context during feature work.
- Estimated operations/evidence docs: **78,220 tokens**.

After:

- `.agentignore` excludes `planning-mds/operations/**` by default.
- `context-map.yaml` exposes only index-level evidence files unless a validation/audit task needs exact evidence.

Reduction:

- Avoided about **78K tokens** during normal feature implementation.

### 4. API and Schema Docs Became Exact-Endpoint Context

Before:

- Full OpenAPI/schema/LOB-schema folders could be loaded up front.
- Estimated API/schema/LOB-schema docs: **41,878 tokens**.

After:

- `api_schema_scope` is non-default.
- The agent loads only exact endpoints or schema files referenced by the feature, tests, KG output, or validator failures.

Reduction:

- Avoided about **42K tokens** of schema context unless the touched endpoint requires it.

### 5. Examples Were Not Loaded by Default

Before:

- Example architecture/screens/personas could be included as general guidance.
- Estimated examples docs: **22,790 tokens**.

After:

- `examples` are explicitly on-demand.
- F0019 did not require example expansion for implementation.

Reduction:

- Avoided about **23K tokens**.

### 6. Full Backend and Frontend Trees Were Replaced by Exact Files

Before:

- A broad source pass could include full `engine`, `experience/src`, and `neuron`.
- Estimated broad source context: **885,484 tokens**.

After:

- Source context was loaded by changed path, KG hint, and targeted search.
- Exact F0019 source/test files represented about **78,194 tokens**.

Reduction:

- Source context reduced by about **807,290 tokens**.
- Source-context reduction: about **91.2%**.

### 7. Feature Scope Prevented Unrelated Active Features From Loading

Before:

- All active feature docs could be pulled even when working only on F0019.
- Active feature docs estimate: **32,657 tokens**.

After:

- F0019-only feature docs estimate: **3,658 tokens**.

Reduction:

- Feature-doc context reduced by about **28,999 tokens**.

### 8. Dev/Test Context Was Loaded Only Where It Mattered

For F0019, the exact test files were loaded:

- `engine/tests/Nebula.Tests/Integration/WorkflowEndpointTests.cs`
- `experience/src/pages/tests/SubmissionDetailPage.integration.test.tsx`
- `experience/src/pages/tests/SubmissionsPage.integration.test.tsx`

Instead of loading the entire test tree, only tests that verify touched behavior were used. This preserved coverage while avoiding broad test-suite prompt loading.

## Files That Implemented the Optimization

Token-loading strategy files in `nebula-insurance-crm`:

| File | Role |
|---|---|
| `.agentignore` | Prevents broad agent discovery/loading of generated outputs, archive docs, evidence, screenshots, coverage, and build outputs |
| `planning-mds/context-map.yaml` | Defines default layers, on-demand layers, forbidden defaults, and token-reporting assumptions |
| `planning-mds/README.md` | Documents the product-local context map convention |
| `README.md` | Points agent sessions to `planning-mds/context-map.yaml` |
| `scripts/validate-context-map.py` | Validates that the context map keeps dangerous/broad defaults out |
| `scripts/tests/test_validate_context_map.py` | Tests context-map validation rules |

## F0019 Exact Context Used After Optimization

Product/feature docs:

- `README.md`
- `lifecycle-stage.yaml`
- `.agentignore`
- `planning-mds/features/REGISTRY.md`
- `planning-mds/features/ROADMAP.md`
- F0019 feature docs under `planning-mds/features/F0019-submission-quoting-proposal-and-approval/`

Backend exact files:

- `engine/src/Nebula.Domain/Entities/Submission.cs`
- `engine/src/Nebula.Infrastructure/Persistence/Configurations/SubmissionConfiguration.cs`
- `engine/src/Nebula.Infrastructure/Persistence/DevSeedData.cs`
- `engine/src/Nebula.Application/DTOs/SubmissionDto.cs`
- `engine/src/Nebula.Application/Services/SubmissionService.cs`
- `engine/src/Nebula.Api/Endpoints/SubmissionEndpoints.cs`
- `engine/src/Nebula.Infrastructure/Persistence/Migrations/20260608093000_F0019_SubmissionQuoteApprovalArchive.cs`
- `engine/tests/Nebula.Tests/Integration/WorkflowEndpointTests.cs`

Frontend exact files:

- `experience/src/features/auth/useCurrentUser.ts`
- `experience/src/features/submissions/types.ts`
- `experience/src/features/submissions/lib/constants.ts`
- `experience/src/features/submissions/index.ts`
- `experience/src/features/submissions/hooks/useUpdateSubmissionQuotePacket.ts`
- `experience/src/features/submissions/hooks/useDecideSubmissionApproval.ts`
- `experience/src/features/submissions/hooks/useArchiveSubmission.ts`
- `experience/src/mocks/submissions.ts`
- `experience/src/mocks/handlers.ts`
- `experience/src/mocks/data.ts`
- `experience/src/pages/SubmissionDetailPage.tsx`
- `experience/src/pages/SubmissionsPage.tsx`
- `experience/src/pages/tests/SubmissionDetailPage.integration.test.tsx`
- `experience/src/pages/tests/SubmissionsPage.integration.test.tsx`
- `experience/src/services/dev-auth.ts`

## Behavior Preservation

The token optimization did not remove safety, validation, or business logic. It changed how context is loaded for agents, not how the CRM runtime behaves.

Preserved behavior:

- Existing public API route style remains.
- Existing submission workflow transition endpoint remains authoritative.
- Existing role checks remain in application services.
- Existing F0019 safety gates remain:
  - quote packet status validation
  - approval requires a started quote packet
  - terminal archive only for allowed states
  - optimistic concurrency with `If-Match`
  - audit timeline events
- Existing frontend hooks and query invalidation patterns are preserved.

## Impact on F0019 Work

The optimization made F0019 implementation more direct:

- The agent did not need to read unrelated features before implementing submission quoting.
- The agent did not need archived feature docs except if explicitly proving provenance.
- Source inspection centered on submission domain, API endpoint, service, DTO, EF config, frontend submission page/hooks, mocks, and tests.
- The later underwriting workflow fix was also localized:
  - existing workflow was discovered instead of reimplemented
  - missing manual path was fixed through dev seed data, dev auth, list navigation, and tests

## Final Comparison

| Metric | Before | After without KG files | After with KG files |
|---|---:|---:|---:|
| Prompt/planning context | 847,544 | 7,761 | 31,625 |
| Source/code context | 885,484 | 78,194 | 78,194 |
| Total estimated context | 1,733,028 | 85,955 | 109,819 |
| Tokens reduced | - | 1,647,073 | 1,623,209 |
| Percent reduced | - | 95.0% | 93.7% |

## Conclusion

For F0019 in `nebula-insurance-crm`, the token optimization reduced estimated context consumption by approximately **93.7% to 95.0%**.

The largest savings came from:

- preventing broad `planning-mds/**` loading,
- excluding archived features and evidence by default,
- avoiding full backend/frontend source-tree loading,
- keeping API/schema/examples on demand,
- and routing feature work through exact F0019 docs plus exact touched code files.

This kept the implementation focused while preserving behavior, validation, auditability, and public interfaces.
