# ACBench

ACBench is a standalone benchmark for evaluating whether an agent can:

- repair code in a local repository fixture
- analyze ops-style incidents
- solve combined tasks that require both ops reasoning and code repair

## Current Scope

The repo currently contains:

- `54` scenarios total
- `9` local scenarios
- `45` GitHub-derived scenarios
- `18` code-only scenarios
- `18` ops-only scenarios
- `18` combined scenarios

Task banks:

- local scenarios: `tasks/scenarios/local/{code,ops,combined}/`
- GitHub-derived scenarios: `tasks/scenarios/github/{code,ops,combined}/`

The current GitHub task bank is built from localized reproductions of
`openclaw/openclaw` issues.

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

## Quick Start

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

Check the environment:

```bash
acbench --doctor
```

Validate a scenario:

```bash
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --validate-scenario
```

## Common Runs

Run one local code scenario with a gold patch:

```bash
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --code-patch patches/billing_pricing_bundle_fix.diff
```

Run one local code scenario with the OpenAI patch agent:

```bash
export OPENAI_API_KEY="<your-key>"
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini --openai-api-key-env OPENAI_API_KEY
```

Run one local code scenario with a Claude patch agent:

```bash
export ANTHROPIC_API_KEY="<your-key>"
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --code-agent-ref acbench.agents.anthropic_code:AnthropicCodePatchAgent --anthropic-model claude-sonnet-4-20250514 --anthropic-api-key-env ANTHROPIC_API_KEY
```

Run one local combined scenario with both agents:

```bash
acbench --scenario tasks/scenarios/local/combined/billing_pricing__checkout_totals_incident.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --aiops-agent-ref acbench.agents.openai_ops:OpenAIOpsAgent --openai-model gpt-4.1-mini --openai-api-key-env OPENAI_API_KEY
```

Run one GitHub-derived combined scenario with both agents:

```bash
acbench --scenario tasks/scenarios/github/combined/openclaw__completion_process_leak_incident.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --aiops-agent-ref acbench.agents.openai_ops:OpenAIOpsAgent --openai-model gpt-4.1-mini --openai-api-key-env OPENAI_API_KEY
```

Run one GitHub-derived combined scenario with Claude code and ops agents:

```bash
acbench --scenario tasks/scenarios/github/combined/openclaw__completion_process_leak_incident.scenario.json --code-agent-ref acbench.agents.anthropic_code:AnthropicCodePatchAgent --aiops-agent-ref acbench.agents.anthropic_ops:AnthropicOpsAgent --anthropic-model claude-sonnet-4-20250514 --anthropic-api-key-env ANTHROPIC_API_KEY
```

Run the full local gold suite:

```bash
acbench --manifest manifests/local_suite.json --predictions predictions/local_gold.json --evaluation-output runs/local_suite_eval.json
```

Run the full GitHub/OpenClaw gold suite:

```bash
acbench --manifest manifests/github_openclaw_extended.json --predictions predictions/github_openclaw_extended_gold.json --evaluation-output runs/github_openclaw_extended_gold_eval.json
```

Run the default local + GitHub OpenAI agent batches from config:

```bash
python scripts/run_openai_agent_evals.py --config configs/openai_direct.local.json
```

Run the default local + GitHub Anthropic agent batches from config:

```bash
cp configs/anthropic_direct.example.json configs/anthropic_direct.local.json
python scripts/run_anthropic_agent_evals.py --config configs/anthropic_direct.local.json
```

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

## What Is Already Validated

This repo has already been exercised successfully across:

- local patch execution
- local code-agent execution
- local combined-agent execution
- GitHub-derived code-agent execution
- GitHub-derived combined-agent execution

## Documentation

- `docs/QUICKSTART.md`
- `docs/COMMANDS.md`
- `docs/SCENARIO_AUTHORING.md`
- `docs/TASK_BANK_REQUIREMENTS.md`
- `docs/ARCHITECTURE.md`

## Notes

- local ops scenarios are rubric-graded incident tasks
- GitHub-derived scenarios currently run on localized fixture reproductions, not live repository checkout
- local config files such as `configs/*.local.json` are ignored by git
