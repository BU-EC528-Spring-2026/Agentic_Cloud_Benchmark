# Architecture

ACBench has four main layers.

## 1. Entry Layer

Top-level files in the repository root:

- `cli.py`: command-line entry point
- `runner.py`: top-level orchestration
- `validate.py`: scenario and backend validation
- `doctor.py`: environment inspection
- `evaluate.py`: batch evaluation
- `report.py`: report generation
- `export.py`: export utilities

## 2. Execution Layer

Directories:

- `executors/`
- `adapters/`

### Executors

Executors are used when ACBench itself performs the work.

Examples:

- `executors/local_code.py`
- `executors/local_ops.py`
- `executors/standalone_code.py`

### Adapters

Adapters are used when ACBench bridges into upstream systems.

Examples:

- `adapters/aiopslab.py`
- `adapters/swebench.py`

## 3. Internal Backend Layer

Directory:

- `backends/`

This is the internal runtime / engine / runner layer used by the execution paths.

### Code backend

- `backends/code/runtime.py`
- `backends/code/engine.py`
- `backends/code/runner.py`
- `backends/code/standalone.py`
- `backends/code/native_upstream.py`

### Ops backend

- `backends/ops/runtime.py`
- `backends/ops/engine.py`
- `backends/ops/runner.py`
- `backends/ops/native_upstream.py`

## 4. Asset Layer

Directories:

- `scenarios/`: benchmark task definitions
- `fixtures/`: local benchmark assets
- `patches/`: reference patches
- `predictions/`: evaluation inputs
- `manifests/`: suite definitions

## Agents

Directory:

- `agents/`

Important examples:

- `agents/openai_code.py`
- `agents/openai_ops.py`

These provide the OpenAI-backed prototype paths.

## Typical Flow

For a standalone local code run:

1. `cli.py` parses the command.
2. `runner.py` loads the scenario.
3. `validate.py` checks the scenario.
4. `executors/local_code.py` runs the task.
5. `agents/openai_code.py` generates a patch if configured.
6. result artifacts are written under `runs/`.

For a live ops bridge run:

1. `cli.py` parses the command.
2. `runner.py` loads the scenario.
3. `adapters/aiopslab.py` bridges into AIOpsLab.
4. `agents/openai_ops.py` produces the action.
5. ACBench normalizes the final result and artifacts under `runs/`.

## Cleanup

Generated artifacts can be cleaned with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\cleanup_generated.ps1
```

## Related Documents

- [README](../README.md)
- [Quickstart](QUICKSTART.md)
- [Scenario Authoring](SCENARIO_AUTHORING.md)
