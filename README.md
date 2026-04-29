# ACBench

ACBench is the **Agentic Cloud Benchmark**: a standalone benchmark for evaluating
whether AI agents can handle realistic cloud engineering work.

It focuses on three capabilities:

- **Code repair**: fix bugs in local repository fixtures and pass tests.
- **Ops incident analysis**: diagnose incident-style failures from logs, symptoms,
  reproduction steps, and service context.
- **Combined workflows**: reason through an incident and then repair the code
  that caused it.

The benchmark is designed to be reproducible. Scenarios are defined as JSON
files, code tasks run against local fixture repositories, ops tasks are graded
with explicit rubrics, and batch evaluations write structured output under
`runs/`.

## Project Website

A static project website is included under `website/`.

To view it locally from the repository root:

```bash
python3 -m http.server 8080 --directory website
```

Then open:

```text
http://localhost:8080
```

Do not paste a Linux/WSL path like
`/mnt/c/Projects/.../website/index.html` directly into the browser address bar;
many browsers treat that as a search query. Use the local server URL above.

Website files:

- `website/index.html`: main page
- `website/styles.css`: page styling
- `website/main.js`: leaderboard rendering
- `website/assets/acbench-hero.png`: hero image

The website is static HTML/CSS/JS, so it can later be deployed with GitHub Pages
or any static hosting service.

### Deploying the Website to GitHub Pages

This repository includes a GitHub Actions workflow at:

```text
.github/workflows/pages.yml
```

When changes to `website/` are pushed to `main`, the workflow uploads the
`website/` directory and deploys it to GitHub Pages.

One-time GitHub setup:

1. Open the GitHub repository in a browser.
2. Go to `Settings` -> `Pages`.
3. Under `Build and deployment`, set `Source` to `GitHub Actions`.
4. Push the repository to `main`.
5. Open the `Actions` tab and wait for `Deploy ACBench Website to GitHub Pages`
   to finish.

For this repository, the expected GitHub Pages URL is:

```text
https://BU-EC528-Spring-2026.github.io/Agentic_Cloud_Benchmark/
```

## Demo Materials

- **Demo 1 slides:**
  https://docs.google.com/presentation/d/18uKBohMB7DRRD-njSvIdS2JKTllzYnA1pyG13W82V_w/edit?usp=sharing
- **Demo 1 quiz:**
  https://forms.gle/cTooPJ68VxmJPmCX9
- **Demo 2 slides:**
  https://docs.google.com/presentation/d/1BiH5X01uw6wMEDQk1UMuV0lAFUlYDSk5Liz-q4Bc_xU/edit?usp=sharing
- **Demo 2 quiz:**
  https://forms.gle/E4e7J8aFsePPqcQK7
- **Demo 2 video:**
  https://drive.google.com/file/d/1etchHhZdAGIIEIhL0kvKwncKADcrtNLP/view?usp=sharing
- **Demo 3 slides:**
  https://docs.google.com/presentation/d/1bZpHWS_KgUSYJzuqrwFnsRE2VB2u3SMkhQwHIYmuPrk/edit?usp=sharing
- **Demo 3 quiz:**
  https://forms.gle/zGEKQNbrwm9oXN4N7
- **Demo 3 video:**
  https://drive.google.com/file/d/1EbAOPPskl-r468DKBclXKqNw7MhoBN5A/view?usp=sharing
- **Final demo slides:**
  https://docs.google.com/presentation/d/1MY85y-QqkPJgykK-D6p7gjqdvWueh6K-1zkNfo0KgD0/edit?usp=sharing
- **Final demo video:**
  https://drive.google.com/file/d/1hQiOzCazdugOyYDJHTGVzLvMd2y1yXnP/view?usp=sharing

## Current Scope

The repository currently contains **61 scenarios**:

| Source | Code | Ops | Combined | Total |
| --- | ---: | ---: | ---: | ---: |
| Local fixtures | 3 | 6 | 3 | 12 |
| GitHub-derived OpenClaw fixtures | 15 | 19 | 15 | 49 |
| **Total** | **18** | **25** | **18** | **61** |

Scenario locations:

- local scenarios: `tasks/scenarios/local/{code,ops,combined}/`
- GitHub-derived scenarios: `tasks/scenarios/github/{code,ops,combined}/`

The GitHub-derived task bank is built from localized reproductions and
OpenClaw-style synthetic incidents. These are not live checkouts of the
upstream repository; they are stable local fixtures and rubrics derived from
real issue patterns.

## Supported Agent Types

ACBench has built-in integrations for live model providers:

- OpenAI
- Azure OpenAI
- Anthropic / Claude

Built-in live agent classes:

- `acbench.agents.openai_code:OpenAICodePatchAgent`
- `acbench.agents.openai_ops:OpenAIOpsAgent`
- `acbench.agents.azure_openai_code:AzureOpenAICodePatchAgent`
- `acbench.agents.azure_openai_ops:AzureOpenAIOpsAgent`
- `acbench.agents.anthropic_code:AnthropicCodePatchAgent`
- `acbench.agents.anthropic_ops:AnthropicOpsAgent`

You can also plug in custom agents with:

- `--code-agent-ref module:Class`
- `--aiops-agent-ref module:Class`
- `--agent-config configs/agents/<profile>.json`

Code agents must expose a patch-generation interface. Ops agents must expose an
analysis interface that returns a structured assessment or rubric-compatible
answer.

## Repository Layout

- `acbench/`: core runtime package
- `acbench/orchestrator/`: CLI, runner, scenario validation, readiness checks
- `acbench/agents/`: OpenAI, Anthropic, scripted, and profile-based agents
- `acbench/executors/`: code and ops execution paths
- `acbench/evaluation/`: manifest evaluation and report helpers
- `acbench/models/`: scenario, runtime, and result schemas
- `tasks/`: scenario definitions and task-bank overview
- `services/`: service docs and local fixture repositories
- `patches/`: gold/reference patches
- `predictions/`: batch evaluation inputs
- `manifests/`: scenario bundles
- `runs/`: generated run outputs
- `configs/`: example provider and agent-profile configs
- `docs/`: deeper documentation
- `website/`: static project website
- `tests/`: unit and integration tests

## Installation

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

After installation, check that the CLI is available **(please watch the final demo video to verify outputs for all these commands)**:

```bash
acbench --doctor
```

## First Things To Try

Validate one scenario without executing it:

```bash
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --validate-scenario
```

Run a dry run:

```bash
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --dry-run
```

Run a local code-repair scenario with the gold patch:

```bash
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --code-patch patches/billing_pricing_bundle_fix.diff
```

This applies the reference patch to the local fixture repository and evaluates
whether the scenario passes its build/test criteria.

## Running With OpenAI Agents

Set your API key:

```bash
export OPENAI_API_KEY="<your-key>"
```

Run one local code scenario:

```bash
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini --openai-api-key-env OPENAI_API_KEY
```

Run one local combined scenario:

```bash
acbench --scenario tasks/scenarios/local/combined/billing_pricing__checkout_totals_incident.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --aiops-agent-ref acbench.agents.openai_ops:OpenAIOpsAgent --openai-model gpt-4.1-mini --openai-api-key-env OPENAI_API_KEY
```

Run one GitHub-derived combined scenario:

```bash
acbench --scenario tasks/scenarios/github/combined/openclaw__completion_process_leak_incident.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --aiops-agent-ref acbench.agents.openai_ops:OpenAIOpsAgent --openai-model gpt-4.1-mini --openai-api-key-env OPENAI_API_KEY
```

Run the default OpenAI batch config:

```bash
cp configs/openai_direct.example.json configs/openai_direct.local.json
python scripts/run_openai_agent_evals.py --config configs/openai_direct.local.json
```

## Running With Azure OpenAI Agents

Set your API key and copy the profile template:

```bash
export AZURE_OPENAI_API_KEY="<your-key>"
cp configs/agents/azure_openai.example.json configs/agents/azure_openai.local.json
```

Edit `configs/agents/azure_openai.local.json` so `model` is your Azure
deployment name and `base_url` is your resource URL, for example
`https://<resource>.openai.azure.com/openai/v1/`.

Run one scenario through the Azure profile:

```bash
acbench --agent-config configs/agents/azure_openai.local.json --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json
```

Run the default Azure batch config:

```bash
cp configs/azure_openai_direct.example.json configs/azure_openai_direct.local.json
python scripts/run_azure_openai_agent_evals.py --config configs/azure_openai_direct.local.json
```

## Running With Anthropic / Claude Agents

Set your API key:

```bash
export ANTHROPIC_API_KEY="<your-key>"
```

Run one local code scenario:

```bash
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --code-agent-ref acbench.agents.anthropic_code:AnthropicCodePatchAgent --anthropic-model claude-sonnet-4-20250514 --anthropic-api-key-env ANTHROPIC_API_KEY
```

Run one GitHub-derived combined scenario:

```bash
acbench --scenario tasks/scenarios/github/combined/openclaw__completion_process_leak_incident.scenario.json --code-agent-ref acbench.agents.anthropic_code:AnthropicCodePatchAgent --aiops-agent-ref acbench.agents.anthropic_ops:AnthropicOpsAgent --anthropic-model claude-sonnet-4-20250514 --anthropic-api-key-env ANTHROPIC_API_KEY
```

Run the default Anthropic batch config:

```bash
cp configs/anthropic_direct.example.json configs/anthropic_direct.local.json
python scripts/run_anthropic_agent_evals.py --config configs/anthropic_direct.local.json
```

Local config files such as `configs/*.local.json` are ignored by git.

## Running With Generic Agent Profiles

Agent profiles let you define code and ops providers in one JSON file.

Example profile files:

- `configs/agents/openai_gpt41mini.example.json`
- `configs/agents/claude_sonnet.example.json`
- `configs/agents/azure_openai.example.json`

Run one scenario through a profile:

```bash
acbench --agent-config configs/agents/claude_sonnet.example.json --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json
```

Run the full local + GitHub suites through a profile:

```bash
python scripts/run_agent_evals.py --agent-config configs/agents/claude_sonnet.example.json
```

## Batch Evaluation

Run the full local gold suite:

```bash
acbench --manifest manifests/local_suite.json --predictions predictions/local_gold.json --evaluation-output runs/local_suite_eval.json
```

Run the full GitHub/OpenClaw gold suite:

```bash
acbench --manifest manifests/github_openclaw_extended.json --predictions predictions/github_openclaw_extended_gold.json --evaluation-output runs/github_openclaw_extended_gold_eval.json
```

Useful manifests:

- `manifests/local_code_suite.json`
- `manifests/local_ops_suite.json`
- `manifests/local_combined_suite.json`
- `manifests/local_suite.json`
- `manifests/github_openclaw_smoke.json`
- `manifests/github_openclaw_extended.json`

## Result Files

Each run creates a timestamped directory under `runs/`.

The main files are:

- `result.json`: full structured result
- `summary.json`: compact summary
- `diagnostics.json`: run metadata and diagnostics

Code runs may also include:

- `openai_generated_patch.diff`
- `anthropic_generated_patch.diff`
- `agent_generated_patch.diff`
- `build.log`
- `test.log`

Ops runs may also include:

- `ops_eval/openai_ops_prompt.txt`
- `ops_eval/openai_ops_response.txt`
- `ops_eval/openai_ops_assessment.json`
- `ops_eval/anthropic_ops_prompt.txt`
- `ops_eval/anthropic_ops_response.txt`
- `ops_eval/anthropic_ops_assessment.json`

Batch evaluations can also write an aggregate JSON file through
`--evaluation-output`.

## Scenario Format

Every production scenario should define:

- `scenario_id`
- `title`
- `mode`
- `source`
- `service`
- `task`
- `visible_context`
- `build`
- `success_criteria`
- `evaluation`
- `constraints`
- `metadata`

Code-capable scenarios include `code_fault`. Ops-capable scenarios include
`ops_fault`.

For authoring rules, see:

- `docs/SCENARIO_AUTHORING.md`
- `docs/TASK_BANK_REQUIREMENTS.md`

## OpenClaw Task Bank

OpenClaw is the current GitHub-derived service family used by ACBench. The
scenarios are localized reproductions and OpenClaw-style incidents based on
real issue patterns.

ACBench uses OpenClaw because the issue set is:

- concrete enough to reproduce
- realistic enough to avoid toy-only tasks
- clear enough to grade with tests or rubrics
- broad enough to support code, ops, and combined workflows

Current OpenClaw coverage:

- `15` code scenarios
- `19` ops scenarios
- `15` combined scenarios
- `49` total GitHub-derived scenarios

The canonical bundle is:

```text
manifests/github_openclaw_extended.json
```

## What Has Been Validated

This repository has already been exercised across:

- local patch execution
- local code-agent execution
- local combined-agent execution
- GitHub-derived code-agent execution
- GitHub-derived combined-agent execution

## More Documentation

- `docs/QUICKSTART.md`
- `docs/COMMANDS.md`
- `docs/SCENARIO_AUTHORING.md`
- `docs/TASK_BANK_REQUIREMENTS.md`
- `docs/ARCHITECTURE.md`
- `tasks/README.md`
- `configs/agents/README.md`

## Notes

- Local ops scenarios are rubric-graded incident tasks.
- GitHub-derived scenarios run on localized fixture reproductions, not live
  repository checkout.
- API-backed agents require provider API keys in the configured environment
  variables.
- The static website is local-only until deployed to a hosting service such as
  GitHub Pages.
