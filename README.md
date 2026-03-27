# ACBench Prototype

Demo 1 Link: https://docs.google.com/presentation/d/18uKBohMB7DRRD-njSvIdS2JKTllzYnA1pyG13W82V_w/edit?usp=sharing ; Quiz Link: https://forms.gle/cTooPJ68VxmJPmCX9

Demo 2 Link: https://docs.google.com/presentation/d/1BiH5X01uw6wMEDQk1UMuV0lAFUlYDSk5Liz-q4Bc_xU/edit?usp=sharing ; Quiz Link: https://forms.gle/E4e7J8aFsePPqcQK7 

ACBench is a benchmark harness for evaluating AI agents on two task families:

- code repair tasks
- ops / incident response tasks

The repository supports two usage modes:

1. Standalone local mode
   - runs with this repository alone
   - includes the local code repair prototype and local benchmark utilities
2. Optional upstream bridge mode
   - adds live integrations with sibling checkouts of `AIOpsLab` and `SWE-bench-Live`
   - enables the real AIOpsLab live ops benchmark and SWE-bench native benchmark paths

If you only clone this repository, you can still run the standalone local prototype.

## What Works Today

With this repository alone, you can:

- run the local code benchmark
- run the OpenAI-backed local code repair prototype
- run the local demo suite
- validate scenarios
- run `--doctor`
- generate result artifacts and reports

With optional sibling checkouts of `AIOpsLab` and `SWE-bench-Live`, you can also:

- run the live AIOpsLab ops benchmark
- run SWE-bench native benchmark scenarios

## Repository Layout

From the repository root:

- `cli.py`: command-line entry point
- `runner.py`: top-level benchmark orchestration
- `validate.py`: scenario and backend validation
- `doctor.py`: environment inspection
- `agents/`: OpenAI-backed and scripted agents
- `executors/`: local and standalone execution paths
- `adapters/`: upstream bridge adapters
- `backends/`: internal code and ops backend layers
- `scenarios/`: benchmark task definitions
- `fixtures/`: local assets such as the buggy repository fixture
- `patches/`: reference patches
- `predictions/`: batch-evaluation inputs
- `docs/`: supplementary documentation

## Getting Started

These steps assume a fresh clone on a new machine.

### 1. Install the base tools

You need:

- `git`
- Python 3.11
- `pip`

Check them:

```bash
git --version
python --version
python -m pip --version
```

If `python` does not point to Python 3.11, use your platform-specific Python 3.11 command instead, such as `python3.11` or `py -3.11`.

### 2. Clone this repository

```bash
git clone <your-repo-url> acbench
cd acbench
```

At this point your directory should look like:

```text
acbench/
  README.md
  requirements.txt
  pyproject.toml
  cli.py
  runner.py
  scenarios/
  fixtures/
  docs/
  ...
```

### 3. Create a virtual environment

Linux / macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

After activation, your shell prompt should show the virtual environment name, usually `.venv`.

### 4. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 5. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Install the repository as an editable package

This step is required if you want commands like `python -m acbench.cli ...` to work from a fresh clone.

```bash
python -m pip install -e .
```

### 7. Verify the package import path

Run:

```bash
python -m acbench.cli --doctor
```

If this runs, the package import path is set up correctly and the repository is ready for standalone local mode.

## Standalone Local Mode

This is the recommended first run on a fresh machine because it only depends on this repository.

### Quick local demo

```bash
python -m acbench.cli --run-local-demo demo_out
```

This writes a demo evaluation bundle under `demo_out/`.

### OpenAI-backed local code prototype

Set your API key first.

Linux / macOS:

```bash
export OPENAI_API_KEY="<your-key>"
```

PowerShell:

```powershell
$env:OPENAI_API_KEY="<your-key>"
```

Then run:

```bash
python -m acbench.cli --scenario scenarios/examples/code_only_local_repo_buggy.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini
```

This benchmark:

- loads the local buggy repository fixture
- asks the model to generate a patch
- applies the patch
- runs build / test commands
- writes standardized result artifacts

## Optional Upstream Bridge Mode

Use this mode only after standalone local mode succeeds.

The bridge integrations are not bundled inside this repository. You must clone the upstream repositories separately.

### Required workspace layout

Put all repositories side by side inside one parent directory:

```text
<workspace>/
  acbench/
  AIOpsLab/
  SWE-bench-Live/
```

Example:

```text
~/projects/
  acbench/
  AIOpsLab/
  SWE-bench-Live/
```

or on Windows:

```text
C:\Projects\
  acbench\
  AIOpsLab\
  SWE-bench-Live\
```

Do not place `AIOpsLab` or `SWE-bench-Live` inside the `acbench/` repository. They should be sibling directories.

### Step-by-step: add `AIOpsLab`

From the parent workspace directory:

```bash
git clone <aiopslab-repo-url> AIOpsLab
```

`AIOpsLab` also has its own environment requirements. At minimum, the live ops path expects:

- Kubernetes
- Helm
- kubectl
- a working cluster context

Check the system tools:

```bash
kubectl version --client
helm version
```

Then return to the `acbench/` repository and run:

```bash
python -m acbench.cli --doctor
```

The doctor output should now show the AIOpsLab-related backend information.

### Step-by-step: add `SWE-bench-Live`

From the parent workspace directory:

```bash
git clone <swe-bench-live-repo-url> SWE-bench-Live
```

The native SWE-bench path expects:

- Docker
- a working Docker daemon

Check Docker:

```bash
docker --version
docker ps
```

Then return to the `acbench/` repository and run:

```bash
python -m acbench.cli --doctor
```

The doctor output should now show the SWE-bench-native-related backend information.

### OpenAI-backed live ops prototype

After `AIOpsLab` is present and your Kubernetes tooling works, run:

```bash
python -m acbench.cli --scenario scenarios/examples/ops_only_astronomy_shop.json --aiops-agent-ref acbench.agents.openai_ops:OpenAIOpsAgent --openai-model gpt-4.1-mini --max-steps 1
```

This path:

- deploys the live service environment
- injects the configured fault
- asks the model for an action
- normalizes the final result into ACBench artifacts

### SWE-bench native scenarios

The repository includes candidate native scenarios under:

- `scenarios/hf_candidates/`

Example:

```bash
python -m acbench.cli --scenario scenarios/hf_candidates/casey__just-2835.scenario.json
```

## Fresh-Machine Reproduction Checklist

If you are trying to reproduce the repository on a new machine, follow this order exactly:

1. Install Git and Python 3.11.
2. Clone `acbench`.
3. Create and activate a virtual environment.
4. Run `python -m pip install -r requirements.txt`.
5. Run `python -m pip install -e .`.
6. Run `python -m acbench.cli --doctor`.
7. Run the standalone local code prototype.
8. Only after that, add optional sibling checkouts of `AIOpsLab` and `SWE-bench-Live`.

## Common Commands

Check the environment:

```bash
python -m acbench.cli --doctor
```

Validate a scenario:

```bash
python -m acbench.cli --validate-scenario scenarios/examples/code_only_local_repo_buggy.json
```

Write a readiness report:

```bash
python -m acbench.cli --write-readiness-report runs/readiness_report.json
```

Run batch evaluation:

```bash
python -m acbench.cli --evaluate-manifest manifests/local_suite.json --predictions predictions/local_gold.json --output runs/local_suite_eval.json
```

## Result Files

Each benchmark run creates a timestamped directory under `runs/`.

The most important files are:

- `result.json`: full structured result
- `summary.json`: concise summary for quick inspection
- `diagnostics.json`: environment and backend diagnostics

Some runs also include:

- `openai_generated_patch.diff`
- `build.log`
- `test.log`
- `aiops_agent_prompt.txt`
- `aiops_agent_response.txt`
- `aiops_agent_action.txt`

## Documentation

This README is intended to be sufficient for first-time setup and first execution.

Supplementary documents:

- [Quickstart](docs/QUICKSTART.md)
- [Commands](docs/COMMANDS.md)
- [Environment](docs/ENVIRONMENT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Scenario Authoring](docs/SCENARIO_AUTHORING.md)
- [Demo Guide](docs/DEMO_GUIDE.md)
- [Prototype Status](docs/PROTOTYPE_STATUS.md)
- [Standalone Status](docs/STANDALONE_STATUS.md)

## Repository Hygiene

Generated directories such as `runs/`, `out/`, `demo_out/`, `.hf_cache/`, and `__pycache__/` should not be committed.

To clean generated artifacts locally:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\cleanup_generated.ps1
```

## Notes

- Linux is the preferred environment for the live integrations.
- PowerShell examples are included because development and debugging were also performed on Windows.
- If you only need the standalone prototype, you do not need `AIOpsLab` or `SWE-bench-Live`.
