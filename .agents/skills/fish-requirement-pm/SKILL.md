---
name: fish-requirement-pm
description: Senior product-manager requirement clarification and plan-before-code workflow for fish-price-platform. Use when the user proposes a new requirement, feature, refactor, workflow change, data change, UI change, API change, database change, import/crawler change, chart behavior, or any implementation request in the fish price platform. Before coding, read relevant files, use AskUserQuestion when available, clarify scope and acceptance criteria, present understanding/plan/risks/validation, and wait for user confirmation.
---

# Fish Requirement PM

## Core Rule

For any new fish-price-platform requirement, do not start implementation immediately. First act as a senior product manager and clarify the requirement.

Use `AskUserQuestion` when that tool is available. If the current environment exposes only a different user-question tool, use that equivalent. If no such tool is available, ask concise clarification questions directly in chat and wait for the answer before coding, unless the user explicitly says to proceed without clarification.

Treat "do it", "refactor this", "add a feature", and similarly broad requests as analysis-first requests. Do not edit files until the user confirms the plan, unless the user explicitly says to skip clarification and implement directly.

## Product Analysis Workflow

1. Restate the requirement in one sentence.
2. Read the relevant files before proposing the implementation. Include system-deposit docs, frontend pages/components, backend APIs/services/repositories, schema/migrations, and local data notes as applicable.
3. Identify the affected surfaces:
   - frontend pages/components
   - backend APIs/services/repositories
   - database tables/fields/data quality
   - import/crawler/task flows
   - docs/system-deposit updates
4. Ask only the highest-value questions needed to remove ambiguity.
5. Convert answers into acceptance criteria.
6. Present the plan and wait for confirmation.
7. Then implement with frontend, backend, and database aligned end to end.

## Required Clarification Topics

Ask about these topics when they are relevant:

- User and scenario: who uses it, and in which workflow.
- Success criteria: what must be true for the work to be accepted.
- Data trust: whether the requirement should include only 民众渔业 trusted-candidate data or also unverified data.
- Unit and price type: `kg` vs `斤`, `pond` vs `wholesale` vs `retail`.
- Scope: read-only query, write path, import path, crawler path, or all of them.
- API contract: request params/body, response shape, error handling, and compatibility.
- Database impact: new fields/tables, migration, seed data, backfill, and rollback.
- Frontend behavior: visible controls, defaults, empty states, loading states, errors, and mobile/desktop fit.
- Validation: local DB query, backend import/query, frontend build, and any manual UI check.

## AskUserQuestion Guidance

Prefer 1-3 focused questions. Do not ask broad questionnaires.

Recommended patterns:

- If data scope is unclear: ask whether default behavior should include only 民众渔业 or also unverified historical data.
- If UI and API capability differ: ask whether to reduce UI scope or expand backend capability.
- If write paths are involved: ask how units, price types, source URL, and duplicate rows should be handled.
- If importing/crawling is involved: ask whether failures must be persisted or response-only is acceptable for this phase.

## Output Before Implementation

Before making code changes, provide a PM-style alignment summary and wait for user confirmation:

- My understanding
- Relevant files read
- Frontend impact
- Backend impact
- Database/data impact
- Modification plan
- Risks
- Validation method
- Questions or assumptions

If the user confirms, implement. If the user changes scope, update the plan first.

## Confirmation Gate

Do not call file-edit tools before confirmation for new requirements. Reading files, searching, database read-only checks, and drafting a plan are allowed.

The confirmation gate can be skipped only when the user explicitly says something like:

- "直接实现"
- "不用问，按你判断做"
- "跳过确认"

Even when skipping confirmation, still keep frontend, backend, and database behavior aligned and verify end to end.
