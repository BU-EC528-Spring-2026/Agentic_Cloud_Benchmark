# ACBench
Demo 1 Link: https://docs.google.com/presentation/d/18uKBohMB7DRRD-njSvIdS2JKTllzYnA1pyG13W82V_w/edit?usp=sharing ; Quiz Link: https://forms.gle/cTooPJ68VxmJPmCX9

Demo 2 Link: https://docs.google.com/presentation/d/1BiH5X01uw6wMEDQk1UMuV0lAFUlYDSk5Liz-q4Bc_xU/edit?usp=sharing ; Quiz Link: https://forms.gle/E4e7J8aFsePPqcQK7 ; Video Link: https://drive.google.com/file/d/1etchHhZdAGIIEIhL0kvKwncKADcrtNLP/view?usp=sharing

Demo 3 Link: https://docs.google.com/presentation/d/1bZpHWS_KgUSYJzuqrwFnsRE2VB2u3SMkhQwHIYmuPrk/edit?usp=sharing ; Quiz Link: https://forms.gle/zGEKQNbrwm9oXN4N7 ; Video Link: https://drive.google.com/drive/folders/1ZWYpDQBv0KxkpEbihAsVFZSNJ3dfkrct?usp=sharing

## What This Agentic Cloud Benchmark (ACBench)

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

- [`samplepkg__local_repo_buggy.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json)
- [`samplepkg__smoke_local.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/standalone/scenarios/code/samplepkg__smoke_local.scenario.json)
- [`astronomy_shop__product_catalog_seed_defect.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/standalone/scenarios/code/astronomy_shop__product_catalog_seed_defect.scenario.json)
- [`samplepkg__local_fixture.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/standalone/scenarios/combined/samplepkg__local_fixture.scenario.json)

Current services:

- [`samplepkg`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/standalone/services/samplepkg)
- [`astronomy_shop`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/standalone/services/astronomy_shop)

## Repository Layout

Main directories:

- [`standalone/scenarios/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/standalone/scenarios): canonical benchmark tasks
- [`standalone/services/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/standalone/services): service metadata and service-level docs
- [`agents/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/agents): OpenAI-backed and scripted agents
- [`executors/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/executors): concrete code and ops execution paths
- [`backends/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/backends): backend/runtime layers used by executors
- [`fixtures/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/fixtures): local assets such as the buggy repository fixture
- [`patches/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/patches): reference patches
- [`predictions/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/predictions): batch evaluation inputs
- [`manifests/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/manifests): batch scenario lists
- [`runs/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/runs): per-run outputs
- [`docs/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/docs): supporting docs

Important top-level files:

- [`cli.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/cli.py): command-line entry point
- [`runner.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/runner.py): top-level benchmark orchestration
- [`validate.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/validate.py): scenario validation
- [`doctor.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/doctor.py): environment inspection
- [`evaluate.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/evaluate.py): manifest/prediction evaluation helpers
- [`report.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/report.py): markdown reporting helpers

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
python -m acbench.cli --doctor
```

### 4. Validate a scenario

```powershell
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --validate-scenario
```

### 5. Run the local batch demo

```powershell
python -m acbench.cli --manifest manifests/local_suite.json --predictions predictions/local_gold.json --evaluation-output runs/local_suite_eval.json
```

That manifest currently evaluates these two scenarios:

- `code_only_local_repo_buggy`
- `combined_local_fixture`

## Common Workflows

### Run one code scenario with a reference patch

```powershell
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --code-patch patches/local_repo_buggy_fix.diff
```

### Run one combined scenario with a reference patch

```powershell
python -m acbench.cli --scenario standalone/scenarios/combined/samplepkg__local_fixture.scenario.json --code-patch patches/local_repo_buggy_fix.diff
```

### Run a code scenario with an OpenAI-backed patch agent

Set your API key first:

```powershell
$env:OPENAI_API_KEY="<your-key>"
```

Then run:

```powershell
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini
```

### Run the built-in local demo bundle

```powershell
python -m acbench.cli --run-local-demo demo_out
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
