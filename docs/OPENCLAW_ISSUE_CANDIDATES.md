# OpenClaw Issue Candidates

This file tracks high-confidence scenario candidates from `openclaw/openclaw`.

These issues were selected because they are concrete, reproducible, have clear acceptance
signals, and can be localized into small ACBench fixtures.

## Count

Current high-confidence candidate count: `13`

## Code-only

- `#63035` device pairing breaks when `pending.json` and `paired.json` drift to `[]`
- `#63076` GPT-5 personality overlay is skipped for aggregator providers
- `#63056` MiniMax usage tracker calls the quota endpoint with `POST` instead of `GET`
- `#63054` `NO_REPLY` leaks into visible output when extra text follows the token
- `#62856` plugin JSON schema circular references trigger recursion and crash validation
- `#62855` `openclaw status --deep` falsely reports healthy memory providers as invalid

## Ops-only

- `#62850` Docker `HEALTHCHECK` marks a healthy gateway as unhealthy
- `#46049` configured long request timeouts are ignored by provider transport
- `#61786` MCP tool calls time out at a hard 60-second limit

## Combined

- `#10864` orphan `openclaw-completion` processes accumulate and cause memory pressure
- `#62840` agent listener fires outside an active run and crashes the gateway
- `#62848` provider failover is too slow, allowing user-facing degradation before fallback
- `#53416` Discord native slash commands acknowledge with `Done` but never send the real response

## First Smoke Picks

The first GitHub-backed smoke scenarios added to this repo are:

- code-only: `#63035`
- ops-only: `#62850`
- combined: `#10864`
