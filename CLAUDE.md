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

1. **Editable zone** (top): `SYSTEM_PROMPT`, `MODEL`, `MAX_TURNS`,
   `create_tools()`, `create_agent()`, `run_task()` — the meta-agent modifies
   these to improve performance.
2. **Fixed zone** (bottom): `to_atif()` and Harbor adapter — infrastructure
   that must not change unless a human asks.

## Key Conventions

- **Single-file harness**: All agent logic lives in `agent.py`. Do not split it
  into multiple modules.
- **uv workflow**: Use `uv run` for all Python commands. Do not use pip directly.
- **Python 3.12+**: Use modern Python features (type hints, match statements).
- **Ruff**: Linter and formatter. Run before committing.
- **pytest-asyncio**: Tests use `asyncio_mode = "auto"` — async test functions
  work without explicit decorators.

## Test Criteria

Tests validate:

1. **Tool creation**: `create_tools()` returns a non-empty list of `FunctionTool`
2. **Agent creation**: `create_agent()` returns an `Agent` with correct name,
   model, and instructions
3. **ATIF serialization**: `to_atif()` produces valid ATIF-v1.6 schema output
   with required fields (schema_version, session_id, agent, steps, final_metrics)
4. **Configuration**: `SYSTEM_PROMPT`, `MODEL`, `MAX_TURNS` are set to expected
   defaults
5. **Edge cases**: Empty results, missing fields, malformed tool calls handled
   gracefully

## Running Experiments

See `program.md` for the full experiment loop protocol. The short version:

1. Establish a baseline run with unmodified `agent.py`
2. Make one improvement at a time
3. Rerun benchmarks, log results to `results.tsv`
4. Keep improvements that increase `passed`; discard others

## Dependencies

Core: `openai-agents`, `pandas`, `openpyxl`, `numpy`
Dev: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`
