# Quickstart

This guide is for someone who has never used the repo before.

## Goal

By the end of this guide you will be able to:

- install the repo
- validate a scenario
- run the local demo suite
- inspect the generated result files

## Setup

From the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

Check that the CLI is available:

```powershell
python -m acbench.cli --doctor
```

## First Safe Command

Validate a scenario without running it:

```powershell
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --validate-scenario
```

## First Real Run

Run the built-in local evaluation bundle:

```powershell
python -m acbench.cli --manifest manifests/local_suite.json --predictions predictions/local_gold.json --evaluation-output runs/local_suite_eval.json
```

Expected behavior:

- the command writes a batch result JSON
- two run directories are created under `runs/`
- each run directory includes `result.json` and `summary.json`

## Run A Single Scenario

Code-only:

```powershell
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --code-patch patches/local_repo_buggy_fix.diff
```

Combined:

```powershell
python -m acbench.cli --scenario standalone/scenarios/combined/samplepkg__local_fixture.scenario.json --code-patch patches/local_repo_buggy_fix.diff
```

## Optional: Run With An OpenAI Agent

```powershell
$env:OPENAI_API_KEY="<your-key>"
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini
```

## Where To Look Next

- See [`COMMANDS.md`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/docs/COMMANDS.md) for a compact command reference.
- See [`SCENARIO_AUTHORING.md`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/docs/SCENARIO_AUTHORING.md) if you want to add tasks.
- See [`ARCHITECTURE.md`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/docs/ARCHITECTURE.md) if you want the code structure.
