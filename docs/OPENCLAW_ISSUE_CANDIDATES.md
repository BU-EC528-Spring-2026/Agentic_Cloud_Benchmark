# OpenClaw Issue Candidates

This file tracks high-confidence scenario candidates from `openclaw/openclaw`.

These issues were selected because they are concrete, reproducible, have clear acceptance
signals, and can be localized into small ACBench fixtures.

## Count

Current localized scenario coverage: `45` scenarios derived from a growing OpenClaw issue set

## Code-only

- `#63035` device pairing breaks when `pending.json` and `paired.json` drift to `[]`
- `#63076` GPT-5 personality overlay is skipped for aggregator providers
- `#63056` MiniMax usage tracker calls the quota endpoint with `POST` instead of `GET`
- `#63054` `NO_REPLY` leaks into visible output when extra text follows the token
- `#62856` plugin JSON schema circular references trigger recursion and crash validation
- `#10864` finished completion workers are not cleaned up when sessions end
- `#62840` late listener events after a run should be skipped instead of crashing
- `#62876` `cron run` can crash after the active run ends
- `#61944` Telegram replies are lost when late listener output crashes delivery recovery
- `#62477` late subprocess stdout reaches the listener after a run ends
- `#62855` fallback memory-status resolution drops config context
- `#62855` memory-status rendering shows missing counts as placeholders
- `#53416` native Discord `/status` replies with `Done` instead of a status card
- `#50111` native Discord shortcuts are routed through the plugin-command fallback
- `#54915` multi-account Discord shortcuts degrade to `Done`

## Ops-only

- `#62850` Docker `HEALTHCHECK` marks a healthy gateway as unhealthy
- `#62848` provider failover is too slow, allowing user-facing degradation before fallback
- `#46049` configured long request timeouts are ignored by provider transport
- `#61786` MCP tool calls time out at a hard 60-second limit
- `#62867` upgrade leaves the CLI dead because a bundled Telegram setup entry is missing
- `#62855` `status --deep` falsely reports healthy memory providers as invalid
- `#53416` Discord slash commands reply with `Done` and no payload
- `#53189` Discord `/status` still replies with `Done` after upgrade
- `#54915` multi-account Discord shortcuts degrade or stop stripping correctly
- `#54681` `/new` slash commands stop resetting the conversation
- `#62840` WhatsApp messages can crash the gateway after the active run ends
- `#62876` `cron run` can trigger late listener crashes
- `#61944` Telegram replies are dropped during late-listener crashes
- `#62793` residual subagent output reaches the listener after cleanup
- `#63220` pi-agent aborts leave late callbacks that corrupt runtime state

## Combined

- `#10864` orphan `openclaw-completion` processes accumulate and cause memory pressure
- `#62840` agent listener fires outside an active run and crashes the gateway
- `#62855` `openclaw status --deep` falsely reports healthy memory providers as invalid
- `#53416` Discord native slash commands acknowledge with `Done` but never send the real response
- `#62848` provider failover is too slow, allowing user-facing degradation before fallback
- `#63035` pairing approval stays broken when state files drift into array form
- `#63076` GPT-5 overlay disappears when routed through aggregator providers
- `#63056` MiniMax usage checks fail because the remains endpoint uses the wrong method
- `#63054` NO_REPLY-prefixed leaked output is still delivered to users
- `#62856` circular schema refs crash validation during startup
- `#62876` late cron-run output crashes the listener after the run ends
- `#61944` Telegram reply delivery is interrupted by late listener output
- `#62477` late subprocess stdout reaches the listener after run teardown
- `#50111` native Discord shortcuts go through the plugin-command `Done` fallback
- `#54915` multi-account Discord shortcuts lose their native response path

## First Smoke Picks

The first GitHub-backed smoke scenarios added to this repo are:

- code-only: `#63035`
- ops-only: `#62850`
- combined: `#10864`
