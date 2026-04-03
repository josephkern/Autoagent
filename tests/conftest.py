"""Shared fixtures and mocks for autoagent tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


@dataclass
class FakeExecResult:
    stdout: str = ""
    stderr: str = ""


def _make_usage(input_tokens: int = 10, output_tokens: int = 5):
    from agents.usage import Usage

    u = Usage()
    u.input_tokens = input_tokens
    u.output_tokens = output_tokens
    u.requests = 1
    return u


@dataclass
class FakeRawResponse:
    usage: object = field(default_factory=_make_usage)


class FakeEnvironment:
    """Mock environment that simulates Harbor's BaseEnvironment."""

    def __init__(self, exec_results: dict[str, FakeExecResult] | None = None):
        self._exec_results = exec_results or {}
        self._default_result = FakeExecResult(stdout="ok")
        self.exec = AsyncMock(side_effect=self._exec_side_effect)

    async def _exec_side_effect(self, command: str, timeout_sec: int = 120) -> FakeExecResult:
        return self._exec_results.get(command, self._default_result)


def make_message_item(text: str) -> SimpleNamespace:
    """Create a fake MessageOutputItem."""
    return SimpleNamespace(
        __class__=type("MessageOutputItem", (), {}),
        raw_item=SimpleNamespace(
            content=[SimpleNamespace(text=text)],
        ),
    )


def make_tool_call_item(name: str, call_id: str, arguments: str) -> SimpleNamespace:
    """Create a fake ToolCallItem."""
    return SimpleNamespace(
        __class__=type("ToolCallItem", (), {}),
        raw_item=SimpleNamespace(name=name, call_id=call_id, arguments=arguments),
    )


def make_tool_output_item(output: str) -> SimpleNamespace:
    """Create a fake ToolCallOutputItem."""
    return SimpleNamespace(
        __class__=type("ToolCallOutputItem", (), {}),
        output=output,
    )


def make_run_result(
    new_items: list | None = None,
    raw_responses: list | None = None,
    last_response_id: str = "resp-001",
) -> SimpleNamespace:
    """Create a fake RunResult."""
    return SimpleNamespace(
        new_items=new_items or [],
        raw_responses=raw_responses or [FakeRawResponse()],
        last_response_id=last_response_id,
    )


@pytest.fixture
def fake_env():
    """Provide a FakeEnvironment instance."""
    return FakeEnvironment()


@pytest.fixture
def fake_env_with_error():
    """Provide an environment where exec raises."""
    env = FakeEnvironment()
    env.exec = AsyncMock(side_effect=RuntimeError("container crashed"))
    return env
