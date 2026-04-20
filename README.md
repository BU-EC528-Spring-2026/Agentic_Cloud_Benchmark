# ACBench

ACBench is a benchmark harness for evaluating AI agents on realistic engineering workflows.

It supports three scenario types:

1. **Code tasks**: fix a bug in a local fixture repository by generating a patch.
2. **Ops tasks**: analyze incident evidence and produce a structured assessment.
3. **Combined tasks**: perform both ops reasoning + code repair in one run.

---

## Why use ACBench?
Use ACBench to:
- Compare model/provider performance on reproducible tasks.
- Run single-scenario experiments quickly from the CLI.
- Evaluate full manifests in batch with consistent outputs.
- Measure both implementation quality (code) and incident reasoning (ops).

---

## Current Benchmark Scope
The repository currently includes **54 scenarios**:

- **Local scenarios**: 9 total
  - 3 code
  - 3 ops
  - 3 combined
- **GitHub-derived scenarios**: 45 total
  - 15 code
  - 15 ops
  - 15 combined

Scenario roots:
- Local: `tasks/scenarios/local/{code,ops,combined}/`
- GitHub-derived: `tasks/scenarios/github/{code,ops,combined}/`

The current GitHub-derived task bank is built from localized reproductions of `openclaw/openclaw` issues.

---

## Repository Layout

- `acbench/`: core runtime package
- `acbench/orchestrator/`: CLI, runner, readiness checks
- `acbench/agents/`: code and ops agents
- `acbench/executors/`: code and ops execution paths
- `acbench/evaluation/`: evaluation and report helpers
- `acbench/models/`: shared scenario, runtime, and result schemas
- `tasks/`: scenario definitions
- `services/`: service docs and fixture repositories
- `patches/`: gold/reference patches
- `predictions/`: batch evaluation inputs
- `manifests/`: scenario bundles
- `runs/`: generated outputs
- `docs/`: supporting docs

---

## Supported Providers
Built-in provider-backed and scaffold agent support includes:
- `openai`
- `anthropic`
- `azure_openai`

See agent config examples in `configs/agents/`.

---

## Quick Start
### 1) Environment setup
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

### 2) Check your environment
```bash
acbench --doctor
```

### 3) Validate one scenario
```bash
acbench \
    --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json \
    --validate-scenario
```

### 4) Run a first scenario (known-good patch)
```bash
acbench \
    --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json \
    --code-patch patches/billing_pricing_bundle_fix.diff
```

---

## Common Runs
### A) Single code task with OpenAI agent
```bash
export OPENAI_API_KEY="<your-key>"
acbench \
  --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json \
  --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent \
  --openai-model gpt-4.1-mini \
  --openai-api-key-env OPENAI_API_KEY
```

### B) Single code task with Antropic agent
```bash
export ANTHROPIC_API_KEY="<your-key>"
acbench \
  --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json \
  --code-agent-ref acbench.agents.anthropic_code:AnthropicCodePatchAgent \
  --anthropic-model claude-sonnet-4-20250514 \
  --anthropic-api-key-env ANTHROPIC_API_KEY
```

### C) Single code task with Azure OpenAI agent

```bash
export AZURE_OPENAI_API_KEY="<your-key>"
acbench \
  --agent-config configs/agents/azure_openai.example.json \
  --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json
```

### D) Combined local scenario with OpenAI code + ops agents
```bash
acbench \
  --scenario tasks/scenarios/local/combined/billing_pricing__checkout_totals_incident.scenario.json \
  --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent \
  --aiops-agent-ref acbench.agents.openai_ops:OpenAIOpsAgent \
  --openai-model gpt-4.1-mini \
  --openai-api-key-env OPENAI_API_KEY
```

### E) Combined GitHub-derived scenario with OpenAI agents
```bash
acbench \
  --scenario tasks/scenarios/github/combined/openclaw__completion_process_leak_incident.scenario.json \
  --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent \
  --aiops-agent-ref acbench.agents.openai_ops:OpenAIOpsAgent \
  --openai-model gpt-4.1-mini \
  --openai-api-key-env OPENAI_API_KEY
```

### F) Combined GitHub-derived scenario with Anthropic agents
```bash
acbench \
  --scenario tasks/scenarios/github/combined/openclaw__completion_process_leak_incident.scenario.json \
  --code-agent-ref acbench.agents.anthropic_code:AnthropicCodePatchAgent \
  --aiops-agent-ref acbench.agents.anthropic_ops:AnthropicOpsAgent \
  --anthropic-model claude-sonnet-4-20250514 \
  --anthropic-api-key-env ANTHROPIC_API_KEY
```

### G) Combined GitHub-derived scenario with Azure OpenAI agent

```bash
export AZURE_OPENAI_API_KEY="<your-key>"
acbench \
  --agent-config configs/agents/azure_openai.example.json \
  --scenario tasks/scenarios/github/combined/openclaw__completion_process_leak_incident.scenario.json
```

---

## Batch Evaluation Workflows

### Run local gold suite
```bash
acbench \
  --manifest manifests/local_suite.json \
  --predictions predictions/local_gold.json \
  --evaluation-output runs/local_suite_eval.json
```

### Run GitHub/OpenClaw extended gold suite
```bash
acbench \
  --manifest manifests/github_openclaw_extended.json \
  --predictions predictions/github_openclaw_extended_gold.json \
  --evaluation-output runs/github_openclaw_extended_gold_eval.json
```

### Run default OpenAI batch script from config
```bash
python scripts/run_openai_agent_evals.py \
  --config configs/openai_direct.local.json
```

### Run default Anthropic batch script from config
```bash
cp configs/anthropic_direct.example.json configs/anthropic_direct.local.json
python scripts/run_anthropic_agent_evals.py \
  --config configs/anthropic_direct.local.json
```

### Run Azure OpenAI batch evaluation through generic agent runner
```bash
export AZURE_OPENAI_API_KEY="<your-key>"
python scripts/run_agent_evals.py \
  --agent-config configs/agents/azure_openai.example.json
```

### Run one scenario through the generic agent profile
```bash
acbench \
  --agent-config configs/agents/claude_sonnet.example.json \
  --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json
```

### Run the full local + GitHub suites through the generic batch runner
```bash
python scripts/run_agent_evals.py \
  --agent-config configs/agents/claude_sonnet.example.json
```

---

## Result Files
Each run creates a timestamped directory under `runs/`.

The main files are:
- `result.json`: full structured result
- `summary.json`: compact summary
- `diagnostics.json`: run metadata and diagnostics

Code runs may also include:
- `openai_generated_patch.diff`
- `anthropic_generated_patch.diff`
- `build.log`
- `test.log`

Ops runs may also include:
- `ops_eval/openai_ops_prompt.txt`
- `ops_eval/openai_ops_response.txt`
- `ops_eval/openai_ops_assessment.json`
- `ops_eval/anthropic_ops_prompt.txt`
- `ops_eval/anthropic_ops_response.txt`
- `ops_eval/anthropic_ops_assessment.json`

---

## Documentation
- `docs/QUICKSTART.md` – setup and first runs
- `docs/COMMANDS.md` – CLI command reference
- `docs/SCENARIO_AUTHORING.md` – how to write scenarios
- `docs/TASK_BANK_REQUIREMENTS.md` – quality requirements for task banks
- `docs/ARCHITECTURE.md` – architecture overview

---

## Demo
**Demo 1**
- https://docs.google.com/presentation/d/18uKBohMB7DRRD-njSvIdS2JKTllzYnA1pyG13W82V_w/edit?usp=sharing
- Quiz Link: https://forms.gle/cTooPJ68VxmJPmCX9

**Demo 2**
- https://docs.google.com/presentation/d/1BiH5X01uw6wMEDQk1UMuV0lAFUlYDSk5Liz-q4Bc_xU/edit?usp=sharing
- Quiz Link: https://forms.gle/E4e7J8aFsePPqcQK7
- Video Link: https://drive.google.com/file/d/1etchHhZdAGIIEIhL0kvKwncKADcrtNLP/view?usp=sharing

**Demo 3**
- https://docs.google.com/presentation/d/1bZpHWS_KgUSYJzuqrwFnsRE2VB2u3SMkhQwHIYmuPrk/edit?usp=sharing
- Quiz Link: https://forms.gle/zGEKQNbrwm9oXN4N7
- Video Link: https://drive.google.com/drive/folders/1ZWYpDQBv0KxkpEbihAsVFZSNJ3dfkrct?usp=sharing

---

## Notes
- local ops scenarios are rubric-graded incident tasks.
- GitHub-derived scenarios run on localized fixture reproductions (not live repository checkout).
- local config files such as `configs/*.local.json` are ignored by git.
