# CLAUDE.md — Autoagent Project Guide

## Project Overview

Autoagent is an autonomous agent engineering framework. A single Python file
(`agent.py`) contains the complete agent harness. A meta-agent iterates on this
file to improve benchmark performance.

## Quick Start

```bash
# Install dependencies (requires uv)
uv sync --all-extras

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

## Project Structure

```
agent.py          — Single-file agent harness (the only file the meta-agent edits)
program.md        — Meta-agent directives and experiment protocol
pyproject.toml    — Project config, dependencies, tool settings
tests/            — Test suite
  test_agent.py   — Unit tests for harness functions
  conftest.py     — Shared fixtures and mocks
```

## Architecture

`agent.py` has two zones separated by a `FIXED ADAPTER BOUNDARY` comment:

1. **Editable zone** (lines 25–73): `SYSTEM_PROMPT`, `MODEL`, `MAX_TURNS`,
   `create_tools()`, `create_agent()`, `run_task()` — the meta-agent modifies
   these to improve performance.
2. **Fixed zone** (line 75+): `to_atif()` — ATIF trajectory serialization
   (195 total lines). Infrastructure that must not change unless a human asks.

### Editable Zone API

| Symbol | Type | Default | Purpose |
|---|---|---|---|
| `SYSTEM_PROMPT` | `str` | `"You are an agent that executes tasks"` | Agent system instructions |
| `MODEL` | `str` | `"gpt-5"` | Model identifier (do not change without human approval) |
| `MAX_TURNS` | `int` | `30` | Maximum agent turns per task |
| `create_tools(environment)` | function | Returns `[run_shell]` | Build the tool list; add new tools here |
| `create_agent(environment)` | function | Returns `Agent(name="autoagent", ...)` | Construct the agent with tools, handoffs, sub-agents |
| `run_task(environment, instruction)` | async function | Calls `Runner.run()` | Orchestration entry point; returns `(result, duration_ms)` |

### Fixed Zone API

| Symbol | Signature | Purpose |
|---|---|---|
| `to_atif` | `(result: object, model: str, duration_ms: int = 0) -> dict` | Converts `RunResult` to ATIF-v1.6 trajectory dict |

### Tools (runtime-discovered)

| Tool | Parameters | Description |
|---|---|---|
| `run_shell` | `{"command": str}` (required) | Run a shell command in the task environment. Returns stdout and stderr. |

### ATIF Output Schema (runtime-verified)

```
top-level keys : schema_version, session_id, agent, steps, final_metrics
agent keys     : name, version, model_name
metrics keys   : total_prompt_tokens, total_completion_tokens, total_cached_tokens,
                 total_cost_usd, total_steps, extra
step keys      : step_id, timestamp, source, message
                 (+ optional: model_name, tool_calls, observation, reasoning_content)
```

### Exports

```python
__all__ = ["create_agent", "create_tools", "run_task", "to_atif"]
```

## Key Conventions

- **Single-file harness**: All agent logic lives in `agent.py`. Do not split it
  into multiple modules.
- **uv workflow**: Use `uv run` for all Python commands. Do not use pip directly.
- **Python 3.12+**: Use modern Python features (type hints, `datetime.UTC`,
  match statements). Ruff enforces `UP` (pyupgrade) rules.
- **Ruff**: Linter and formatter. Rules: `E`, `F`, `I`, `N`, `W`, `UP`.
  Line length: 100. Run before committing.
- **pytest-asyncio**: Tests use `asyncio_mode = "auto"` — async test functions
  work without explicit decorators.

## Test Criteria

Tests are organized into four classes in `tests/test_agent.py` (15 tests total):

### TestConfiguration (3 tests)
- `SYSTEM_PROMPT` is a non-empty string
- `MODEL` equals `"gpt-5"`
- `MAX_TURNS` is a positive integer

### TestCreateTools (2 tests)
- `create_tools()` returns a non-empty list
- The list contains a tool named `"run_shell"`

### TestCreateAgent (4 tests)
- Returns an agent with `name == "autoagent"`
- Agent's `model` matches `MODEL`
- Agent's `instructions` match `SYSTEM_PROMPT`
- Agent has at least one tool

### TestToAtif (6 tests)
- Empty result produces valid ATIF-v1.6 with required fields
  (`schema_version`, `session_id`, `agent`, `steps`, `final_metrics`)
- Step IDs are sequential (1, 2, 3, ...)
- Token counts propagate into `final_metrics`
- Missing `last_response_id` falls back to `"unknown"`
- Default `duration_ms` is `0`
- Output is JSON-serializable

## Test Fixtures (tests/conftest.py)

| Fixture / Helper | Purpose |
|---|---|
| `FakeEnvironment` | Mock environment with async `exec()` returning `FakeExecResult` |
| `FakeRawResponse` | Wraps a real `Usage` object for `to_atif()` tests |
| `_make_usage(input_tokens, output_tokens)` | Factory for real `agents.usage.Usage` instances |
| `make_run_result(new_items, raw_responses, last_response_id)` | Factory for fake `RunResult` objects |
| `fake_env` (fixture) | Provides a `FakeEnvironment` instance |
| `fake_env_with_error` (fixture) | Environment where `exec()` raises `RuntimeError` |

## Running Experiments

See `program.md` for the full experiment loop protocol. The short version:

1. Establish a baseline run with unmodified `agent.py`
2. Make one improvement at a time
3. Rerun benchmarks, log results to `results.tsv`
4. Keep improvements that increase `passed`; discard others

## Dependencies

Core: `openai-agents`, `pandas`, `openpyxl`, `numpy`
Dev: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`
