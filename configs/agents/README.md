# Agent Profiles

These files define one generic agent entrypoint for ACBench.

Each profile can define:

- `code`: how to run code-repair tasks
- `ops`: how to run ops-style tasks

Supported built-in providers:

- `openai`
- `anthropic`

Typical usage:

```bash
acbench --agent-config configs/agents/claude_sonnet.example.json --scenario tasks/scenarios/local/code/billing_pricing__bundle_discount_threshold.scenario.json
```

Batch usage:

```bash
python3 scripts/run_agent_evals.py --agent-config configs/agents/claude_sonnet.example.json
```
