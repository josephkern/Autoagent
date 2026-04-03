"""Tests for the autoagent harness (agent.py)."""

from __future__ import annotations

import json

from agent import (
    MAX_TURNS,
    MODEL,
    SYSTEM_PROMPT,
    create_agent,
    create_tools,
    to_atif,
)
from tests.conftest import (
    FakeRawResponse,
    _make_usage,
    make_run_result,
)

# ---------------------------------------------------------------------------
# Configuration defaults
# ---------------------------------------------------------------------------


class TestConfiguration:
    def test_system_prompt_is_set(self):
        assert isinstance(SYSTEM_PROMPT, str)
        assert len(SYSTEM_PROMPT) > 0

    def test_model_is_gpt5(self):
        assert MODEL == "gpt-5"

    def test_max_turns_is_positive(self):
        assert isinstance(MAX_TURNS, int)
        assert MAX_TURNS > 0


# ---------------------------------------------------------------------------
# Tool creation
# ---------------------------------------------------------------------------


class TestCreateTools:
    def test_returns_nonempty_list(self, fake_env):
        tools = create_tools(fake_env)
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_run_shell_tool_exists(self, fake_env):
        tools = create_tools(fake_env)
        names = [t.name for t in tools]
        assert "run_shell" in names


# ---------------------------------------------------------------------------
# Agent creation
# ---------------------------------------------------------------------------


class TestCreateAgent:
    def test_returns_agent(self, fake_env):
        agent = create_agent(fake_env)
        assert agent.name == "autoagent"

    def test_agent_has_correct_model(self, fake_env):
        agent = create_agent(fake_env)
        assert agent.model == MODEL

    def test_agent_has_instructions(self, fake_env):
        agent = create_agent(fake_env)
        assert agent.instructions == SYSTEM_PROMPT

    def test_agent_has_tools(self, fake_env):
        agent = create_agent(fake_env)
        assert len(agent.tools) > 0


# ---------------------------------------------------------------------------
# ATIF serialization
# ---------------------------------------------------------------------------


class TestToAtif:
    def test_empty_result_produces_valid_atif(self):
        result = make_run_result(new_items=[], raw_responses=[FakeRawResponse()])
        atif = to_atif(result, model="gpt-5", duration_ms=100)

        assert atif["schema_version"] == "ATIF-v1.6"
        assert atif["session_id"] == "resp-001"
        assert atif["agent"]["name"] == "autoagent"
        assert atif["agent"]["version"] == "0.1.0"
        assert atif["agent"]["model_name"] == "gpt-5"
        assert len(atif["steps"]) >= 1
        assert atif["final_metrics"]["total_steps"] >= 1

    def test_step_ids_are_sequential(self):
        result = make_run_result()
        atif = to_atif(result, model="gpt-5")
        ids = [s["step_id"] for s in atif["steps"]]
        assert ids == list(range(1, len(ids) + 1))

    def test_metrics_include_token_counts(self):
        result = make_run_result(raw_responses=[FakeRawResponse(usage=_make_usage(100, 50))])
        atif = to_atif(result, model="gpt-5", duration_ms=500)
        metrics = atif["final_metrics"]
        assert metrics["total_prompt_tokens"] == 100
        assert metrics["total_completion_tokens"] == 50
        assert metrics["extra"]["duration_ms"] == 500

    def test_missing_response_id_falls_back(self):
        result = make_run_result(last_response_id=None)
        atif = to_atif(result, model="gpt-5")
        assert atif["session_id"] == "unknown"

    def test_duration_default_zero(self):
        result = make_run_result()
        atif = to_atif(result, model="gpt-5")
        assert atif["final_metrics"]["extra"]["duration_ms"] == 0

    def test_serializable_to_json(self):
        result = make_run_result()
        atif = to_atif(result, model="gpt-5", duration_ms=42)
        dumped = json.dumps(atif)
        assert isinstance(dumped, str)
        loaded = json.loads(dumped)
        assert loaded["schema_version"] == "ATIF-v1.6"
