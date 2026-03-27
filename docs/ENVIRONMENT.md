# Environment

This document explains which environments are required for each ACBench capability.

## Baseline Requirements

For the standalone local prototype:

- Python 3.11
- `pip`
- a virtual environment
- Python dependencies from `requirements.txt`
- editable install via `python -m pip install -e .`

Optional, depending on what you run:

- OpenAI API key for OpenAI-backed agent runs

## Standalone Local Mode

This mode requires only this repository.

Supported capabilities:

- local code benchmark
- OpenAI-backed local code repair prototype
- local demo suite
- local scenario validation
- local report generation

This mode does not require:

- `AIOpsLab`
- `SWE-bench-Live`
- Kubernetes
- Docker for the local code fixture path

## Optional Upstream Bridge Mode

This mode adds live integrations through sibling repositories.

Expected workspace layout:

```text
<workspace>/
  acbench/
  AIOpsLab/
  SWE-bench-Live/
```

### AIOpsLab Live Ops Path

Requires:

- sibling `AIOpsLab/` checkout
- Kubernetes
- Helm
- kubectl

Used for:

- `scenarios/examples/ops_only_astronomy_shop.json`

### SWE-bench Native Path

Requires:

- sibling `SWE-bench-Live/` checkout
- Docker

Used for:

- scenarios under `scenarios/hf_candidates/`

## Notes on Platform Choice

- Linux is preferred for live integrations.
- PowerShell commands are documented because local development also occurred on Windows.
- The standalone local prototype is the least fragile path and should be your first verification target on a fresh machine.
