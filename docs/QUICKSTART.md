# Quickstart

This document is a shorter companion to the main [README](../README.md). Use the README if you are setting up the repository from scratch on a new machine.

## Fastest Successful Path

From the repository root:

1. Create and activate a Python 3.11 virtual environment.
2. Install dependencies.
3. Install the repository as an editable package.
4. Run `--doctor`.
5. Run the standalone local code prototype.

## Setup

Linux / macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

Verify:

```bash
python -m acbench.cli --doctor
```

## First Recommended Command

Run the standalone local code prototype:

```bash
python -m acbench.cli --scenario scenarios/examples/code_only_local_repo_buggy.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini
```

Set `OPENAI_API_KEY` before running the command.

## Local Demo Suite

```bash
python -m acbench.cli --run-local-demo demo_out
```

This is a safe local check that does not require `AIOpsLab` or `SWE-bench-Live`.

## Live Ops Prototype

This requires:

- sibling `AIOpsLab/` checkout
- Kubernetes
- Helm
- kubectl

Command:

```bash
python -m acbench.cli --scenario scenarios/examples/ops_only_astronomy_shop.json --aiops-agent-ref acbench.agents.openai_ops:OpenAIOpsAgent --openai-model gpt-4.1-mini --max-steps 1
```

## Most Useful Output Files

After a run, inspect:

- `runs/<timestamp>/result.json`
- `runs/<timestamp>/summary.json`
- `runs/<timestamp>/diagnostics.json`

For code runs, also inspect:

- `openai_generated_patch.diff`
- `build.log`
- `test.log`

For live ops runs, also inspect:

- `aiops_agent_prompt.txt`
- `aiops_agent_response.txt`
- `aiops_agent_action.txt`

## Where To Read Next

- [Commands](COMMANDS.md)
- [Environment](ENVIRONMENT.md)
- [Architecture](ARCHITECTURE.md)
- [Scenario Authoring](SCENARIO_AUTHORING.md)
