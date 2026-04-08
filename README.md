# ACBench

ACBench is a standalone benchmark repository for evaluating an agent's ability to:

- repair code in a local repository fixture
- handle ops-style incident tasks in a local runtime
- solve combined tasks that require both code repair and ops reasoning

This repository is standalone-only. It does not depend on sibling repositories such as AIOpsLab or SWE-bench-Live.

## What This Repo Contains

Today the repo includes:

- `4` standalone scenarios total
- `3` code scenarios
- `0` ops-only scenarios
- `1` combined scenario
- `2` service families

Current scenarios:

- [`samplepkg__local_repo_buggy.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks/scenarios/code/samplepkg__local_repo_buggy.scenario.json)
- [`samplepkg__smoke_local.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks/scenarios/code/samplepkg__smoke_local.scenario.json)
- [`astronomy_shop__product_catalog_seed_defect.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks/scenarios/code/astronomy_shop__product_catalog_seed_defect.scenario.json)
- [`samplepkg__local_fixture.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks/scenarios/combined/samplepkg__local_fixture.scenario.json)

Current services:

- [`samplepkg`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/services/catalog/samplepkg)
- [`astronomy_shop`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/services/catalog/astronomy_shop)

## Repository Layout

Main directories:

- [`acbench/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench): core Python package
- [`acbench/orchestrator/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench/orchestrator): CLI, run flow, readiness, and demo/export entrypoints
- [`tasks/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks): canonical benchmark task definitions
- [`acbench/agents/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench/agents): OpenAI-backed and scripted agents
- [`acbench/executors/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench/executors): concrete code and ops execution paths
- [`services/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/services): service docs and local fixture repositories
- [`acbench/evaluation/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench/evaluation): batch scoring and report generation
- [`acbench/models/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench/models): shared runtime, scenario, and result schemas
- [`patches/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/patches): reference patches
- [`predictions/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/predictions): batch evaluation inputs
- [`manifests/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/manifests): batch scenario lists
- [`runs/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/runs): per-run outputs
- [`docs/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/docs): supporting docs

Important code files:

- [`acbench/__init__.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench/__init__.py): package root
- [`acbench/paths.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench/paths.py): shared repository path helpers
- [`acbench/orchestrator/runner.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench/orchestrator/runner.py): canonical benchmark orchestration
- [`acbench/orchestrator/cli.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench/orchestrator/cli.py): canonical CLI implementation
- [`acbench/evaluation/evaluate.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench/evaluation/evaluate.py): manifest/prediction evaluation helpers
- [`acbench/evaluation/report.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/acbench/evaluation/report.py): markdown reporting helpers

## Quick Start

Everything below assumes you are in:

```powershell
C:\Projects\ACBench\Agentic_Cloud_Benchmark
```

### 1. Create and activate a virtual environment

PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. Install the repo

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

### 3. Check the environment

```powershell
acbench --doctor
```

### 4. Validate a scenario

```powershell
acbench --scenario tasks/scenarios/code/samplepkg__local_repo_buggy.scenario.json --validate-scenario
```

### 5. Run the local batch demo

```powershell
acbench --manifest manifests/local_suite.json --predictions predictions/local_gold.json --evaluation-output runs/local_suite_eval.json
```

That manifest currently evaluates these two scenarios:

- `code_only_local_repo_buggy`
- `combined_local_fixture`

## Common Workflows

### Run one code scenario with a reference patch

```powershell
acbench --scenario tasks/scenarios/code/samplepkg__local_repo_buggy.scenario.json --code-patch patches/local_repo_buggy_fix.diff
```

### Run one combined scenario with a reference patch

```powershell
acbench --scenario tasks/scenarios/combined/samplepkg__local_fixture.scenario.json --code-patch patches/local_repo_buggy_fix.diff
```

### Run a code scenario with an OpenAI-backed patch agent

Set your API key first:

```powershell
$env:OPENAI_API_KEY="<your-key>"
```

Then run:

```powershell
acbench --scenario tasks/scenarios/code/samplepkg__local_repo_buggy.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini
```

### Run the built-in local demo bundle

```powershell
acbench --run-local-demo demo_out
```

## How Results Are Written

Each run creates a timestamped directory under [`runs/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/runs).

The most important files are:

- `result.json`: full structured output
- `summary.json`: compact result summary
- `diagnostics.json`: environment and backend diagnostics

Some runs may also include:

- `openai_generated_patch.diff`
- `build.log`
- `test.log`

## How To Read Success

For local standalone runs, the most important indicators are:

- top-level `status`
- `code.success`
- `code.build_success`
- `code.test_success`
- `ops.success` for combined or future ops scenarios

If `status` is `success` and the relevant `code.success` or `ops.success` fields are true, the run succeeded.

## Running Tests

Run the current standalone regression suite:

```powershell
python -m unittest tests.test_standalone_layout tests.test_evaluate tests.test_runner tests.test_cli tests.test_combined_local tests.test_standalone_code_executor tests.test_ops_engine tests.test_ops_runtime tests.test_ops_runner tests.test_result_model -v
```

## Documentation Map

Start here first:

- [`README.md`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/README.md)

Use these when you need more detail:

- [`docs/QUICKSTART.md`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/docs/QUICKSTART.md)
- [`docs/COMMANDS.md`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/docs/COMMANDS.md)
- [`docs/SCENARIO_AUTHORING.md`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/docs/SCENARIO_AUTHORING.md)
- [`docs/ARCHITECTURE.md`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/docs/ARCHITECTURE.md)

## Current Limitations

- There are currently no standalone ops-only scenarios.
- The benchmark suite is still small.
- `astronomy_shop` currently has placeholder-style coverage compared with `samplepkg`.
- The current local demo manifest contains only two scenarios.

## Repository Hygiene

Generated outputs such as `runs/`, `out/`, `demo_out/`, `tmp/`, `.hf_cache/`, and `__pycache__/` should not be committed.
