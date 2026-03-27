# Demo Guide

This guide is for recording or presenting the prototype.

## Recommended Story

Present ACBench as a benchmark layer with two modes:

1. standalone local mode
2. optional upstream bridge mode

The cleanest demo is:

1. show the standalone local code prototype
2. show the live AIOpsLab ops prototype

This demonstrates both benchmark families without requiring you to explain every internal module.

## Demo 1: Standalone Local Code Prototype

Command:

```bash
python -m acbench.cli --scenario scenarios/examples/code_only_local_repo_buggy.json --code-agent-ref acbench.agents.openai_code:OpenAICodePatchAgent --openai-model gpt-4.1-mini
```

What to say:

- ACBench loads a local buggy repository fixture.
- The model generates a patch.
- ACBench applies the patch, runs tests, and scores the outcome.
- This path works with this repository alone.

What to show afterward:

- `runs/<timestamp>/summary.json`
- `runs/<timestamp>/openai_generated_patch.diff`
- `runs/<timestamp>/result.json`

## Demo 2: Live AIOpsLab Ops Prototype

Requirements:

- sibling `AIOpsLab/` checkout
- Kubernetes
- Helm
- kubectl

Command:

```bash
python -m acbench.cli --scenario scenarios/examples/ops_only_astronomy_shop.json --aiops-agent-ref acbench.agents.openai_ops:OpenAIOpsAgent --openai-model gpt-4.1-mini --max-steps 1
```

What to say:

- ACBench launches a live ops benchmark path through AIOpsLab.
- The service is deployed.
- A fault is injected.
- The agent submits a detection decision.
- ACBench normalizes the final score and artifacts.

What to show afterward:

- `runs/<timestamp>/summary.json`
- `runs/<timestamp>/aiops_agent_prompt.txt`
- `runs/<timestamp>/aiops_agent_response.txt`
- `runs/<timestamp>/result.json`

## Suggested Closing Message

Use a short summary:

> Standalone mode proves that ACBench already works as an independent benchmark prototype.
> Optional bridge mode shows that the same interface can also evaluate live upstream systems.

## Practical Recording Advice

- Record from the repository root.
- Keep the terminal font large.
- Do not leave long infrastructure waits unedited if you are recording a short demo.
- Show the final `summary.json` after each run; it is easier to read than the full `result.json`.
