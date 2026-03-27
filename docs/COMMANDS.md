# Commands

All commands below assume you are running from the repository root and have already activated your Python environment.

## Environment Checks

Run the environment doctor:

```bash
python -m acbench.cli --doctor
```

Write a readiness report:

```bash
python -m acbench.cli --write-readiness-report runs/readiness_report.json
```

Validate a scenario:

```bash
python -m acbench.cli --validate-scenario scenarios/examples/code_only_local_repo_buggy.json
```

## Standalone Local Prototype

Run the local demo suite:

```bash
python -m acbench.cli --run-local-demo demo_out
```

Run the OpenAI-backed local code benchmark:

```bash
python -m acbench.cli --scenario scenarios/examples/code_only_local_repo_buggy.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini
```

Run the local combined fixture with a reference patch:

```bash
python -m acbench.cli --scenario scenarios/examples/combined_local_fixture.json --code-patch patches/local_repo_buggy_fix.diff
```

## Optional Upstream Bridge Commands

Run the AIOpsLab live ops prototype:

```bash
python -m acbench.cli --scenario scenarios/examples/ops_only_astronomy_shop.json --aiops-agent-ref acbench.agents.openai_ops:OpenAIOpsAgent --openai-model gpt-4.1-mini --max-steps 1
```

Run a native SWE-bench candidate scenario:

```bash
python -m acbench.cli --scenario scenarios/hf_candidates/casey__just-2835.scenario.json
```

## Evaluation and Reporting

Run batch evaluation:

```bash
python -m acbench.cli --evaluate-manifest manifests/local_suite.json --predictions predictions/local_gold.json --output runs/local_suite_eval.json
```

Generate a markdown report from an evaluation output:

```bash
python -m acbench.cli --report-json runs/local_suite_eval.json --report-md runs/local_suite_report.md
```

## Export Utilities

Export a scenario as a SWE-bench-style instance:

```bash
python -m acbench.cli --export-swebench-instance scenarios/examples/code_only_local_repo_buggy.json --output out/code_only_local_repo_buggy.instance.json
```
