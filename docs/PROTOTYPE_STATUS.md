# Prototype Status

## Current State

The first prototype milestone is complete.

ACBench currently supports:

- an OpenAI-backed standalone local code repair benchmark
- a live AIOpsLab-backed ops detection benchmark
- standardized result artifacts under `runs/`

## What Has Been Demonstrated

### Standalone local code path

ACBench can:

- load a buggy local repository fixture
- ask the model to generate a patch
- apply the patch
- run build and test commands
- score the result

### Live ops bridge path

ACBench can:

- invoke a live AIOpsLab scenario
- deploy the service environment
- inject the fault
- ask the model for an action
- normalize the final result

## What Is Still Optional

The repository still treats these as optional bridge integrations rather than standalone internal runtimes:

- `AIOpsLab` live ops orchestration
- `SWE-bench-Live` native execution

## Recommended Interpretation

ACBench should be understood as:

- a standalone benchmark prototype in local mode
- plus optional upstream bridge integrations for live workflows
