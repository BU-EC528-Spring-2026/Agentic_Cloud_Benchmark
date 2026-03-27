# Scenario Authoring

Scenarios define benchmark tasks. They live under `scenarios/`.

## Where To Start

The easiest way to learn the format is to read the example scenarios:

- `scenarios/examples/code_only_local_repo_buggy.json`
- `scenarios/examples/combined_local_fixture.json`
- `scenarios/examples/ops_only_astronomy_shop.json`

## Scenario Categories

### Local examples

Directory:

- `scenarios/examples/`

Use these for:

- learning the format
- local standalone prototype runs
- creating new local tasks

### Native SWE-bench candidates

Directory:

- `scenarios/hf_candidates/`

Use these for:

- native SWE-bench benchmark tasks
- optional upstream bridge workflows

## Typical Local Code Scenario Inputs

A local code scenario usually specifies:

- repository path
- build commands
- test commands
- success criteria
- code fault metadata

The local buggy repository example uses:

- `fixtures/local_repo_buggy`

## Typical Ops Scenario Inputs

An ops scenario usually specifies:

- service or problem metadata
- backend selection
- ops fault metadata
- evaluation mode

The live astronomy-shop example uses:

- `scenarios/examples/ops_only_astronomy_shop.json`

## Validation

Validate a scenario with:

```bash
python -m acbench.cli --validate-scenario scenarios/examples/code_only_local_repo_buggy.json
```

## Export

You can export a scenario into a SWE-bench-style instance with:

```bash
python -m acbench.cli --export-swebench-instance scenarios/examples/code_only_local_repo_buggy.json --output out/code_only_local_repo_buggy.instance.json
```

## Recommended Workflow

1. Copy an existing example from `scenarios/examples/`.
2. Edit the fields you need.
3. Validate the scenario.
4. Run it locally.
5. Add tests if you are changing scenario-loading behavior.

## Related Documents

- [README](../README.md)
- [Quickstart](QUICKSTART.md)
- [Commands](COMMANDS.md)
