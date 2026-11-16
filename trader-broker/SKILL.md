---
name: trader-broker
description: >-
  Order Executor for any AI agent. Submits risk-passed Alpaca orders autonomously,
  paper by default, without per-order user approval. Prepares exact broker inputs,
  records authorization and fills, and closes day trades by flat_by. Use after
  trader-risk passes, or to execute or close a trade. Manual mode is opt-in.
argument-hint: "[order number]"
---

# trader-broker

## Execution policy

Autonomous execution is the default for Alpaca when `autonomous` is omitted or
true in `trader/config.json`. The AI agent should continue to submission after
risk PASS without asking for a fresh yes. This applies to entries, exits,
scheduled tasks and background runs. Do not invent a user reply: use `authorize`.
Only an explicit `"autonomous": false` selects manual confirmation via `approve`.
Host policies and broker permissions still apply; this skill cannot grant them.

Run commands from the repository root, or use the absolute installed script
path. Keep the working directory at the project containing your `trader/` data.

```bash
python3 trader-broker/ticket.py show
python3 trader-broker/ticket.py authorize --index 1
python3 trader-broker/ticket.py result --index 1 --status placed --broker-id ID
python3 trader-broker/ticket.py fill --symbol TSLA --side buy --qty 8 --price 364.20
python3 trader-broker/ticket.py flatten --symbol TSLA --qty 8
python3 trader-broker/ticket.py log
```

`ticket.py` prepares and logs orders; it does not contact a broker. The running
agent calls the broker tool with the exact printed JSON. A successful local
authorization is not proof of submission or a fill.

## Connect Alpaca once

Use Alpaca's official MCP server: https://github.com/alpacahq/alpaca-mcp-server.
`mcp_config.example.json` is a generic MCP example, not a universal host config.
Map its command, arguments and environment into your agent's supported settings.

- Command: `uvx`; arguments: `alpaca-mcp-server`.
- Store API keys in the host's secret environment/configuration, never in chat.
- `ALPACA_PAPER_TRADE=true` selects paper trading. Never change it automatically.
- `ALPACA_TOOLSETS=account,trading,stock-data` exposes trading as well as reads.
- Allow `place_stock_order` and `cancel_order_by_id` for unattended execution.
  Discover the installed server's actual tool names; host prefixes may differ.
- Expose account, position, open-order, clock and quote reads for reconciliation.
  Leave unrelated options, crypto and bulk-account operations disabled.
- Reload the server and verify its account and effective paper/live endpoint.

For Hermes Agent, use its supported `hermes mcp configure alpaca-paper` flow
if that is the configured server name. Inspect local help if the command or
server differs. Check both the server's `ALPACA_TOOLSETS` environment and
Hermes's `mcp_servers.alpaca-paper.tools.include` allowlist; read-only toolsets
or allowlists cannot submit orders. Configure unattended tool permissions using
the installed Hermes version's supported settings. Reload the MCP connection
and start a new chat to discard old loaded skill text. See `SETUP.md`.

An integration that only drafts orders for provider review (including some
Interactive Brokers connectors) is not an autonomous execution backend. Use
Alpaca for this workflow; do not claim to bypass provider review.

## Execute one order

1. Use a single active trading runner for this account and data directory.
   Reconcile broker cash, positions and open orders into `trader/portfolio.json`.
2. Run trader-risk on the final order. Only a PASS for today's exact fingerprint
   is READY. BLOCK, stale checks or changed tickets require a fresh check.
3. Run `ticket.py show`, then `ticket.py authorize --index N`. If autonomy is
   explicitly false, instead show the ticket, obtain its yes and use
   `ticket.py approve --index N --reply "the actual reply"`.
4. After successful authorization, call `place_stock_order` with exactly the
   printed JSON. Autonomous mode needs no per-order chat confirmation.
5. Record `ticket.py result --index N --status placed --broker-id ID`, or
   `--status denied|failed --note REASON`. Record actual fills with
   `--filled-qty Q --filled-price P` or `ticket.py fill`. Never assume a fill.
6. After a timeout or ambiguous response, reconcile broker orders before any
   further write. Never blindly retry. Local fingerprint checks are not a
   broker idempotency guarantee. Sync state and rerun risk before the next order.

## Monitor and close

Register `alerts.py add --from-plan` and monitor positions through the host's
scheduler or running agent. Alpaca bracket legs handle the stop and target.
Record their actual fills. At `flat_by`, reconcile holdings and open legs,
run `ticket.py flatten --symbol SYMBOL --qty Q`, then trader-risk and the same
autonomous authorization workflow. Cancel only this position's open bracket
legs, verify cancellation and remaining shares, then submit the closing ticket.

The tools do not install a scheduler or support concurrent account runners.
Do not claim local tests demonstrate unattended broker execution. Multi-runner
reservations, broker idempotency and a persistent kill switch need additional
execution infrastructure; this pack does not implement those guarantees.

## Limits

- Never increase risk limits, change paper/live mode or widen instrument permissions
  automatically. Autonomous execution uses the existing configured limits.
- Never submit without exact-order trader-risk PASS and recorded authorization.
- Never read, repeat or commit API keys or passwords.
- Never call bulk cancel/close, option or crypto tools through this workflow.
- A market or stop order can fill worse than the planned price.
- Education and tooling, not financial advice. A PASS is a rules check.
