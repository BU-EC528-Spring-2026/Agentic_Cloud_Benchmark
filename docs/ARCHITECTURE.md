# Architecture

## High-Level Flow

The execution path is:

1. `cli.py` parses command-line inputs.
2. `validate.py` loads and normalizes the scenario.
3. `runner.py` selects the correct standalone executor.
4. The executor runs code and/or ops work.
5. Result artifacts are written under `runs/`.

## Main Code Areas

- [`cli.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/cli.py): command-line interface
- [`runner.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/runner.py): top-level orchestration
- [`validate.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/validate.py): scenario validation and readiness checks
- [`doctor.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/doctor.py): environment inspection
- [`evaluate.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/evaluate.py): manifest evaluation helpers
- [`report.py`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/report.py): markdown reporting

## Scenario And Service Assets

- [`standalone/scenarios/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/standalone/scenarios): benchmark definitions
- [`standalone/services/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/standalone/services): service-level docs and metadata
- [`fixtures/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/fixtures): local fixture repositories and assets
- [`patches/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/patches): reference patches

## Execution Layers

- [`executors/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/executors): concrete execution paths
- [`backends/code/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/backends/code): code backend helpers
- [`backends/ops/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/backends/ops): ops backend helpers
- [`agents/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/agents): patch or action generators
- [`models/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/models): shared scenario/result/runtime models

## Current Benchmark Shape

Current scenario inventory:

- `3` code scenarios
- `0` ops-only scenarios
- `1` combined scenario

Current service families:

- `samplepkg`
- `astronomy_shop`

## Result Artifacts

Each run directory typically includes:

- `result.json`
- `summary.json`
- `diagnostics.json`

Code runs may also include:

- `openai_generated_patch.diff`
- `build.log`
- `test.log`
