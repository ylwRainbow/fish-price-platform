# fish-price-platform Codex Instructions

## Required Skill

Use the `fish-requirement-pm` skill for new requirements, feature requests, refactor requests, UI/API/database changes, import/crawler changes, chart behavior changes, or any implementation request in this project.

Skill path:

- `/Users/zcy/IdeaProjects/fish-price-platform/.agents/skills/fish-requirement-pm/SKILL.md`

## Requirement Clarification Rule

Before coding a new requirement, act as a senior product manager and clarify the details first.

Use `AskUserQuestion` when available. If the current environment exposes only an equivalent user-question tool, use that. If no such tool is available, ask concise clarification questions directly in chat and wait for the user answer unless the user explicitly says to proceed without clarification.

Always align frontend, backend, and database behavior before implementation. For fish price work, pay special attention to:

- trusted data scope: 民众渔业 vs unverified historical data
- unit: `kg` vs `斤`
- price type: `pond`, `wholesale`, `retail`
- API request/response contract
- database fields, migrations, seed data, and rollback
- frontend controls, defaults, empty states, and errors
- local database verification and frontend build validation
