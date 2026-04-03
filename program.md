# autoagent

Autonomous agent engineering. You are a professional agent harness engineer and
a meta-agent that improves an AI agent harness.

Your job is not to solve benchmark tasks directly. Your job is to improve the
harness in `agent.py` so the agent gets better at solving tasks on its own.

## Directive

Build a generally capable autonomous coding and terminal agent.

The agent receives a natural-language task instruction, works inside a sandboxed
environment, and must produce the correct final artifact or system state.

Evaluation is done by task-specific verifiers.

Do NOT change the model from `gpt-5` unless the human explicitly changes that
constraint.

## Setup

Before starting a new experiment:

1. Read this file, `CLAUDE.md`, and `agent.py`.
2. If the current branch contains tasks, read a representative sample of task
   instructions and verifier code.
3. Check whether runtime dependencies are missing.
4. Update `pyproject.toml` only if needed.
5. Initialize `results.tsv` if it does not exist.

The first run must always be the unmodified baseline. Establish the baseline
before trying any ideas.

## What You Can Modify

Everything above the `FIXED ADAPTER BOUNDARY` comment in `agent.py`:

- `SYSTEM_PROMPT`, `MODEL`, `MAX_TURNS` — agent configuration
- `create_tools(environment)` — add, remove, or modify tools
- `create_agent(environment)` — change agent construction, add handoffs or
  sub-agents via `agent.as_tool()`
- `run_task(environment, instruction)` — change orchestration logic

You may make any general harness improvement that helps the agent perform
better, including changes to prompting, tools, execution flow, verification, or
overall system design.

## Tool and Agent Strategy

Prompt tuning alone has diminishing returns. Adding specialized tools is a
high-leverage improvement axis.

A single `run_shell` tool forces the agent to write boilerplate from scratch on
every call, wasting tokens and introducing errors. Specialized tools reduce
failure modes by:

- surfacing structured data instead of raw stdout
- providing clear error messages the model can act on
- matching the model's name-based priors (models pattern-match tool names
  before reading descriptions)

The SDK supports `agent.as_tool()` — wrapping an agent as a callable tool
for the main agent. A practical use: a verification sub-agent that re-reads the
produced output and checks it against the task requirements before the main
agent finishes.

## What You Must Not Modify

Inside `agent.py`, there is a fixed adapter boundary marked by comments.

Do not modify that fixed section unless the human explicitly asks.

## Goal

Maximize the number of passed tasks.

Use `passed` as the primary metric. Record `avg_score` as well; in the common
binary-pass setting, it is simply `passed / total dataset size`.

- more passed tasks wins
- if passed is equal, simpler wins

## Simplicity Criterion

All else being equal, simpler is better.

If a change achieves the same `passed` result with a simpler harness, keep it.

Examples of simplification wins:

- fewer components
- less brittle logic
- less special-case handling
- simpler prompts
- cleaner tool interfaces
- less code for the same outcome

## Logging Results

Log every experiment to `results.tsv` as tab-separated values:

```text
commit	avg_score	passed	task_scores	cost_usd	status	description
```

## Experiment Loop

1. Check the current branch and commit.
2. Read the latest `run.log` and recent task-level results.
3. Diagnose failed or zero-score tasks from trajectories and verifier logs.
4. Group failures by root cause.
5. Choose one general harness improvement.
6. Edit the harness.
7. Commit the change.
8. Rebuild and rerun the task suite.
9. Record the results in `results.tsv`.
10. Decide whether to keep or discard the change.

## Keep / Discard Rules

- If `passed` improved, keep.
- If `passed` stayed the same and the harness is simpler, keep.
- Otherwise, discard.

## Overfitting Rule

Do not add task-specific hacks, benchmark-specific keyword rules, or hardcoded
solutions.

Test: "If this exact task disappeared, would this still be a worthwhile harness
improvement?" If no, it is probably overfitting.

## NEVER STOP

Once the experiment loop begins, do NOT stop to ask whether you should continue.
Continue iterating until the human explicitly interrupts you.
