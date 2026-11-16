---
name: day-trader
description: >-
  Autonomous day-trading workflow for an AI agent using Alpaca. Orchestrates
  eleven bundled skills from research through risk-checked entries and exits.
  Paper trading by default; no per-order chat approval in autonomous mode.
---

# Day trader: autonomous workflow

Read `SETUP.md` on installation and `trader-broker/SKILL.md` before execution.
This is the entry point for hosts that install one skill from the repository.
The `trader-*/SKILL.md` files supply detailed steps and scripts.

## Authorization

With the owner's instruction to run this workflow, autonomously select and
execute qualifying trades within the configured strategy and risk limits.
`autonomous` defaults to true, including in preserved configs without the field.
No fresh per-order yes is required for entries, exits or scheduled/background
execution. Only an explicit `"autonomous": false` selects manual confirmation.
Use `ticket.py authorize`; never fabricate a user reply for `approve`.

Risk limits, account scope and host/broker permissions remain binding. A missing
write tool is a setup issue: identify its exact config and use the host's
supported permission workflow with owner authorization. Never bypass host policy.

## Workflow

1. Run one active runner per account. Use the configured symbols and strategy;
   scanner -> news -> entry -> exit -> timemachine -> budget -> risk -> broker.
2. Read each corresponding bundled skill. Use completed bars, a stop and a
   flat-by time. Reject setups that fail the configured rules.
3. Reconcile broker positions, cash and open orders; run trader-risk on the
   final ticket. Authorize and submit only the exact PASS ticket.
4. Record broker results and actual fills. Reconcile ambiguous submissions
   instead of retrying blindly. Refresh risk and broker state before another entry.
5. Monitor bracket fills and close remaining positions by flat_by using the
   same autonomous authorization path. No arbitrary trade is needed for setup.

## Installation and reload

Preserve .env files, credentials, config, portfolio and state when updating.
Run `python3 configure.py` from the repository root with the project's working
folder selected, then reload skills and MCP tools and start a fresh host chat.
Do not keep a duplicate older day-trading skill active. The setup helper only
updates local trading config; it does not change host permissions or place orders.

These skills require a running agent/scheduler and an order-capable broker
connection. Offline tests do not establish broker connectivity or profitability.
