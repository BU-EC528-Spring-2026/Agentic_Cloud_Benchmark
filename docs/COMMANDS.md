# Commands

All commands assume:

- you are in `C:\Projects\ACBench\Agentic_Cloud_Benchmark`
- the virtual environment is activated

## Environment

```powershell
acbench --doctor
acbench --write-readiness-report runs/readiness_report.json
```

## Scenario Validation

```powershell
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --validate-scenario
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --check-readiness
```

## Single-Scenario Execution

Code-only with a patch:

```powershell
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --code-patch patches/billing_pricing_bundle_fix.diff
```

Combined with a patch:

```powershell
acbench --scenario tasks/scenarios/local/combined/billing_pricing__checkout_totals_incident.scenario.json --code-patch patches/billing_pricing_bundle_fix.diff
```

Ops-only validation:

```powershell
acbench --scenario tasks/scenarios/local/ops/cache_api__stale_index_alert.scenario.json --validate-scenario
```

Code-only with an OpenAI agent:

```powershell
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini
```

Dry run:

```powershell
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --dry-run
```

## Batch Evaluation

```powershell
acbench --manifest manifests/local_suite.json --predictions predictions/local_gold.json --evaluation-output runs/local_suite_eval.json
acbench --manifest manifests/github_openclaw_smoke.json --predictions predictions/github_openclaw_gold.json --evaluation-output runs/github_openclaw_smoke_eval.json
```

## OpenAI Agent Batch Runs

Edit `configs/openai_direct.local.json`, then run:

```powershell
python scripts/run_openai_agent_evals.py --config configs/openai_direct.local.json
```

## Export

```powershell
acbench --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json --export-code-instance out/code_only_billing_pricing_bundle_threshold.instance.json
```

## Reports

From an evaluation JSON:

```powershell
acbench --evaluation-json runs/local_suite_eval.json --write-markdown-report runs/local_suite_eval.md
```

From one run directory:

```powershell
acbench --run-dir runs/code_only_billing_pricing_bundle_threshold-YYYYMMDD-HHMMSS-XXXXXX --write-run-markdown-report runs/code_only_billing_pricing_bundle_threshold_report.md
```

## Demo

```powershell
acbench --run-local-demo demo_out
```
