# Commands

All commands assume:

- you are in `C:\Projects\ACBench\Agentic_Cloud_Benchmark`
- the virtual environment is activated

## Environment

```powershell
python -m acbench.cli --doctor
python -m acbench.cli --write-readiness-report runs/readiness_report.json
```

## Scenario Validation

```powershell
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --validate-scenario
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --check-readiness
```

## Single-Scenario Execution

Code-only with a patch:

```powershell
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --code-patch patches/local_repo_buggy_fix.diff
```

Combined with a patch:

```powershell
python -m acbench.cli --scenario standalone/scenarios/combined/samplepkg__local_fixture.scenario.json --code-patch patches/local_repo_buggy_fix.diff
```

Code-only with an OpenAI agent:

```powershell
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini
```

Dry run:

```powershell
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --dry-run
```

## Batch Evaluation

```powershell
python -m acbench.cli --manifest manifests/local_suite.json --predictions predictions/local_gold.json --evaluation-output runs/local_suite_eval.json
```

## Export

```powershell
python -m acbench.cli --scenario standalone/scenarios/code/samplepkg__local_repo_buggy.scenario.json --export-code-instance out/code_only_local_repo_buggy.instance.json
```

## Reports

From an evaluation JSON:

```powershell
python -m acbench.cli --evaluation-json runs/local_suite_eval.json --write-markdown-report runs/local_suite_eval.md
```

From one run directory:

```powershell
python -m acbench.cli --run-dir runs/code_only_local_repo_buggy-YYYYMMDD-HHMMSS-XXXXXX --write-run-markdown-report runs/code_only_local_repo_buggy_report.md
```

## Demo

```powershell
python -m acbench.cli --run-local-demo demo_out
```
