# Scenario Authoring

All supported benchmark scenarios now live under [`tasks/scenarios/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks/scenarios).

Current subdirectories:

- [`tasks/scenarios/code/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks/scenarios/code)
- [`tasks/scenarios/combined/`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks/scenarios/combined)

There are currently no standalone ops-only scenarios in the repo.

## Start From Existing Files

Reference code scenarios:

- [`samplepkg__local_repo_buggy.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks/scenarios/code/samplepkg__local_repo_buggy.scenario.json)
- [`samplepkg__smoke_local.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks/scenarios/code/samplepkg__smoke_local.scenario.json)
- [`astronomy_shop__product_catalog_seed_defect.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks/scenarios/code/astronomy_shop__product_catalog_seed_defect.scenario.json)

Reference combined scenario:

- [`samplepkg__local_fixture.scenario.json`](c:/Projects/ACBench/Agentic_Cloud_Benchmark/tasks/scenarios/combined/samplepkg__local_fixture.scenario.json)

## Typical Code Scenario Fields

Important fields:

- `scenario_id`
- `title`
- `mode`
- `service`
- `code_fault`
- `build.rebuild_cmds`
- `build.test_cmds`
- `success_criteria`
- `metrics`
- `gold_patch_path`

Code scenarios generally point at a local repository through:

- `service.repository_path`

## Typical Combined Scenario Fields

Combined scenarios include all major code fields plus:

- `ops_fault`
- ops-related success criteria such as detection, localization, and repair

## Authoring Rules

- Put new code-only tasks under `tasks/scenarios/code/`.
- Put new combined tasks under `tasks/scenarios/combined/`.
- Keep scenario filenames stable and descriptive.
- Prefer one service family per scenario.
- Keep build and test commands directly runnable from the copied workspace.

## Validation

Validate every new scenario before running it:

```powershell
acbench --scenario tasks/scenarios/code/samplepkg__local_repo_buggy.scenario.json --validate-scenario
```

Check whether the environment is ready:

```powershell
acbench --scenario tasks/scenarios/code/samplepkg__local_repo_buggy.scenario.json --check-readiness
```
