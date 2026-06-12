---
name: fish-requirement-pm
description: Senior product-manager requirement clarification workflow for fish-price-platform. Use when the user proposes a new requirement, feature, refactor, workflow change, data change, UI change, API change, database change, import/crawler change, chart behavior, or any implementation request in the fish price platform. Before coding, use AskUserQuestion when available to clarify scope, success criteria, data/API/database impacts, and edge cases.
---

# Fish Requirement PM

## Core Rule

For any new fish-price-platform requirement, do not start implementation immediately. First act as a senior product manager and clarify the requirement.

Use `AskUserQuestion` when that tool is available. If the current environment exposes only a different user-question tool, use that equivalent. If no such tool is available, ask concise clarification questions directly in chat and wait for the answer before coding, unless the user explicitly says to proceed without clarification.

## Product Analysis Workflow

1. Restate the requirement in one sentence.
2. Identify the affected surfaces:
   - frontend pages/components
   - backend APIs/services/repositories
   - database tables/fields/data quality
   - import/crawler/task flows
   - docs/system-deposit updates
3. Ask only the highest-value questions needed to remove ambiguity.
4. Convert answers into acceptance criteria.
5. Then implement with frontend, backend, and database aligned end to end.

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

Before making code changes, provide a short PM-style alignment summary:

- Goal
- In scope
- Out of scope
- Acceptance criteria
- Assumptions

Keep it concise. After the user answers, execute the implementation and verify it end to end.
