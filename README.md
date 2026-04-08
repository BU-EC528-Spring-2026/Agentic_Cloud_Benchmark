# ACBench

ACBench is a standalone benchmark repository for evaluating an agent's ability to:

- repair code in a local repository fixture
- handle ops-style incident tasks in a local runtime
- solve combined tasks that require both code repair and ops reasoning

This repository is standalone-only. It does not depend on sibling repositories such as AIOpsLab or SWE-bench-Live.

## What This Repo Contains

Today the repo includes:

- `12` standalone scenarios total
- `9` local scenarios
- `3` GitHub-backed smoke scenarios
- `4` code scenarios
- `4` ops-only scenarios
- `4` combined scenarios
- `7` service families

Current scenarios:

- Local scenarios now live under `tasks/scenarios/local/{code,ops,combined}/`
- GitHub-backed scenarios now live under `tasks/scenarios/github/{code,ops,combined}/`
- The first GitHub smoke set is:
  - `openclaw__pairing_state_array_persistence.scenario.json`
  - `openclaw__docker_healthcheck_false_unhealthy.scenario.json`
  - `openclaw__completion_process_leak_incident.scenario.json`

Current services:

- [`billing_pricing`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/services/catalog/billing_pricing)
- [`feature_router`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/services/catalog/feature_router)
- [`maintenance_window`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/services/catalog/maintenance_window)
- [`cache_api`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/services/catalog/cache_api)
- [`queue_worker`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/services/catalog/queue_worker)
- [`payments_api`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/services/catalog/payments_api)
- [`openclaw`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/services/catalog/openclaw)

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
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --validate-scenario
```

### 5. Run the local batch demo

```powershell
acbench --manifest manifests/local_suite.json --predictions predictions/local_gold.json --evaluation-output runs/local_suite_eval.json
```

That manifest currently evaluates all `9` local scenarios across code-only, ops-only, and combined modes.

GitHub-backed smoke evaluation:

```powershell
acbench --manifest manifests/github_openclaw_smoke.json --predictions predictions/github_openclaw_gold.json --evaluation-output runs/github_openclaw_smoke_eval.json
```

Run both local and GitHub manifests with the OpenAI patch agent:

```powershell
python scripts/run_openai_agent_evals.py --config configs/openai_direct.local.json
```

## Common Workflows

### Run one code scenario with a reference patch

```powershell
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --code-patch patches/billing_pricing_bundle_fix.diff
```

### Run one combined scenario with a reference patch

```powershell
acbench --scenario tasks/scenarios/local/combined/billing_pricing__checkout_totals_incident.scenario.json --code-patch patches/billing_pricing_bundle_fix.diff
```

### Run a code scenario with an OpenAI-backed patch agent

Set your API key first:

```powershell
$env:OPENAI_API_KEY="<your-key>"
```

Then run:

```powershell
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini
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
- `ops.success` for ops-only and combined scenarios

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

- Local ops scenarios are still synthetic even though they now have dedicated task-bank entries.
- GitHub-backed scenarios currently run through localized fixture snapshots rather than live repository checkout.
- The OpenAI batch runner expects a local config file; copy `configs/openai_direct.example.json` or edit `configs/openai_direct.local.json`.

## Repository Hygiene

Generated outputs such as `runs/`, `out/`, `demo_out/`, `tmp/`, `.hf_cache/`, and `__pycache__/` should not be committed.
