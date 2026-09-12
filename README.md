# Travel Planner + AI GitHub Issue Resolution System

This repository now contains:

1. A legacy AI travel planner CLI.
2. A production-oriented, three-agent GitHub Issue Resolution workflow with a mandatory developer approval gate.

---

## Architecture Overview

```text
GitHub Issue
   |
   v
[Agent 1: Issue Detection]
   |
   v
[Agent 2: Issue Validation]
   |
   v
[Developer Approval Gate] --reject--> [REJECTED]
   |
  approve
   v
[Agent 3: Issue Resolution]
   |
   v
Code changes -> tests -> PR creation -> manual developer merge
```

### Core modules

- `src/agents/`
  - `issue_detector.py` (read-only issue ingestion + dedupe)
  - `issue_validator.py` (analysis-only validation)
  - `issue_resolver.py` (approval-guarded implementation flow)
  - `executors.py` (local git/test/PR integration points)
- `src/orchestration/`
  - `state_machine.py` (allowed transitions)
  - `state_store.py` (SQLite durable state + approvals)
  - `approval_gate.py` (developer approval logic)
  - `workflow.py` (end-to-end orchestration)
- `src/github/`
  - `client.py` (GitHub API client)
  - `issues.py` (issue read/search/comment operations)
  - `pull_requests.py` (branch + PR operations)
- `src/llm/`
  - `provider.py` (provider abstraction)
  - `factory.py` (env-driven provider selection)
- `src/mcp/`
  - `tools_read.py` (read-only toolset)
  - `tools_write.py` (write toolset with approval checks)
  - `server.py` (tool dispatch)
- `src/models/schemas.py` (typed payloads and reports)
- `src/notifications/developer_notify.py` (approval notifications)
- `src/main.py` (workflow CLI)

---

## Agent Responsibilities

### Agent 1 — Issue Detection Agent
- Detects new issues.
- Builds structured `IssuePayload`.
- Prevents duplicate processing.
- Does **not** modify code or create PRs.

### Agent 2 — Issue Validation Agent
- Reads issue details/comments.
- Inspects repository code.
- Flags duplicates/reproducibility.
- Produces structured `ValidationReport`.
- Analysis-only (no code changes).

### Developer Approval Gate
- Receives validation summary.
- Explicit approve/reject decision.
- Resolver cannot execute write actions unless approved.

### Agent 3 — Issue Resolution Agent
- Verifies approval first.
- Creates issue branch.
- Applies minimal targeted changes (executor integration point).
- Runs tests.
- Creates PR (or returns manual PR requirement if not configured).

---

## Workflow States

`NEW -> DETECTED -> VALIDATING -> VALID -> WAITING_FOR_APPROVAL -> APPROVED -> IMPLEMENTING -> TESTING -> READY_FOR_REVIEW -> PR_CREATED -> MERGED`

Failure states:
`INVALID, DUPLICATE, REJECTED, IMPLEMENTATION_FAILED, TEST_FAILED, NEEDS_HUMAN_REVIEW`

---

## Environment Variables

Required:

- `GITHUB_REPOSITORY` (`owner/repo`)
- `GITHUB_TOKEN` (for GitHub API calls)
- `LLM_PROVIDER` (default: `OPENAI`)
- `LLM_MODEL` (default: `gpt-4o`)
- `OPENAI_API_KEY` (required when `LLM_PROVIDER=OPENAI`)
- `STATE_DB_PATH` (default: `state/workflow_state.db`)
- `LOG_LEVEL` (default: `INFO`)
- `APPROVAL_CHANNEL` (default: `stdout`)

Optional:

- `MAX_RETRIES`
- `GITHUB_API_BASE_URL`

---

## Security Model

- No API keys are hardcoded.
- Secrets are loaded from environment.
- Structured logs are sanitized for sensitive fields.
- Agent 3 write actions are blocked unless explicit approval exists.
- Pull requests are never auto-merged.
- Permissions should follow least privilege:
  - Agent 1/2: read-focused scopes
  - Agent 3: write scopes only after approval

---

## MCP Tooling Model

- Read tools (`src/mcp/tools_read.py`) expose issue discovery and inspection operations.
- Write tools (`src/mcp/tools_write.py`) enforce approval checks before branch/PR operations.
- `src/mcp/server.py` provides modular dispatch.

---

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running the workflow

```bash
python -m src.main process --issue 123
python -m src.main approve --issue 123 --by yourname --reason "validated"
python -m src.main resume --issue 123
python -m src.main reject --issue 123 --by yourname --reason "not reproducible"
```

---

## Testing

Run unit/integration-style workflow tests with mocks:

```bash
python -m pytest -q
```

Test coverage includes:
- new issue detection
- duplicate detection
- valid/invalid validation
- approval/rejection paths
- resolver blocked without approval
- resolver after approval
- test failure handling
- implementation failure handling
- MCP write gating
- state persistence
- LLM failure fallback

---

## Legacy Travel Planner CLI

The original CLI remains available at:

- `travel planner/travel.py`

It now uses the shared LLM provider abstraction in `src/llm/`.
