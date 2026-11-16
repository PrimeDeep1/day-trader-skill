---
name: trader-broker
description: >-
  Order Executor. Autonomously submits risk-passed Alpaca orders when configured,
  paper by default. Records authorization, orders and fills; closes positions
  by flat_by. Use after trader-risk passes or to execute or close a trade.
argument-hint: "[order number]"
---

# trader-broker

Only this skill submits orders. With `"autonomous": true` in
`trader/config.json` and `"broker": "alpaca"`, execute without per-order user
confirmation, including scheduled/background runs. Never invent a user reply.
With autonomy absent or false, use `ticket.py approve --reply` with the user's
actual explicit yes. IBKR retains its provider-required review.

`${CLAUDE_SKILL_DIR}` is this skill's folder. `ticket.py` prepares and logs
orders; it does not contact a broker. A running agent must call the broker.

## Setup A: Alpaca (official MCP server, Claude Desktop)

Alpaca's own server is github.com/alpacahq/alpaca-mcp-server (MIT). It runs on
the user's computer inside Claude Desktop. It is not in Claude's connector
directory. It trades on a **paper** account unless told otherwise. Checked
against its source on 2026-10-20 (version 2.4.0).

1. The user makes an Alpaca account and creates **paper trading** API keys in
   the Alpaca dashboard. Paper keys are separate from live keys.
2. The user installs `uv` (it provides `uvx`), from docs.astral.sh/uv.
3. In Claude Desktop: Settings > Developer > Edit Config. That opens
   `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`,
   Windows: `%APPDATA%\Claude\`). The user adds this block (also in
   `claude_desktop_config.example.json` here) and types their own keys into the file:

```json
{
  "mcpServers": {
    "alpaca": {
      "command": "uvx",
      "args": ["alpaca-mcp-server"],
      "env": {
        "ALPACA_API_KEY": "paste your paper key here, in this file only",
        "ALPACA_SECRET_KEY": "paste your paper secret here, in this file only",
        "ALPACA_PAPER_TRADE": "true",
        "ALPACA_TOOLSETS": "account,trading,stock-data"
      }
    }
  }
}
```

   The `env` block hands the keys to the server as environment variables.
   **Keys never go in the chat.** Never ask for them, never read this file
   back into the conversation, and if the user pastes a key anyway, tell them
   to delete that message and make new keys in the Alpaca dashboard.
   `ALPACA_PAPER_TRADE` is already true by default; writing it makes it
   visible. `ALPACA_TOOLSETS` is optional and hides the tools they do not need.
4. Restart Claude Desktop.
5. **Set the tool permissions.** Customize > Connectors (Settings > Connectors
   in older versions), open alpaca, and for each tool pick Always allow, Needs
   approval or Blocked:
   - `place_stock_order`: **Always allow** for configured autonomy; otherwise Needs approval.
   - every other tool that places, changes, cancels or closes anything
     (`cancel_order_by_id`, `replace_order_by_id`, `close_position`,
     `update_account_config`): Needs approval. For autonomy, allow only
     `cancel_order_by_id` as needed to close a bracket position.
   - `place_option_order`, `place_crypto_order`, `close_all_positions`,
     `cancel_all_orders`, `exercise_options_position`,
     `do_not_exercise_options_position`: **Blocked** unless the user has a
     reason and says so.
   - read-only tools (`get_account_info`, `get_all_positions`, `get_open_position`,
     `get_orders`, `get_clock`, `get_stock_snapshot`, `get_stock_latest_quote`):
     Always allow is fine.
6. Check it: ask Claude for the Alpaca account info (read only) and confirm
   in the Alpaca dashboard that it is the paper account.

In Claude Code, for configured autonomy use `.claude/settings.json`:
`"permissions": {"allow": ["mcp__alpaca__place_stock_order", "mcp__alpaca__cancel_order_by_id"]}`.
Otherwise keep the order tool in `ask`. Host or broker restrictions still apply;
these instructions cannot override them.

**Bracket orders on Alpaca.** `place_stock_order` takes
`take_profit_limit_price` and `stop_loss_stop_price` (and an optional
`stop_loss_limit_price`). When either is there, the server sets
`order_class` to "bracket" by itself; trader-budget writes it anyway so the
ticket shows it. A bracket is whole shares only, with `time_in_force` day or
gtc. After the entry fills, the stop-loss and the take-profit wait at the
broker as two orders that cancel each other. They are day orders too, so they
end at the close: one more reason to be flat by then.

## Setup B: Interactive Brokers (connector in Claude's directory)

Interactive Brokers publishes a verified connector: claude.ai/directory/interactive-brokers
(connector URL `https://api.ibkr.com/v1/api/mcp`). Add it from Customize >
Connectors > Browse connectors and sign in to IBKR there, not in the chat.
Its listing says Claude can draft trade instructions that are sent to the
user's IBKR account for their review and approval, and that Claude never
submits orders directly to the market. So with IBKR the final yes happens in
IBKR as well. Set `"broker": "ibkr"` in `trader/config.json`. Set its tools
that draft orders to Needs approval too.

## Execution workflow

1. Read `trader/config.json`, sync broker cash, positions and open orders into
   `trader/portfolio.json`, and run `/trader-risk` on the final orders.
2. Run `ticket.py show`. Only READY tickets can proceed. For each ticket in
   autonomous Alpaca mode run `ticket.py authorize --index N`. Otherwise show
   the ticket, ask for its explicit yes, and use `approve --index N --reply`.
3. Only after successful authorization, call `place_stock_order` with exactly
   the printed JSON. Do not ask for another yes in autonomous mode.
4. Record `ticket.py result --index N --status placed --broker-id ID`, or
   `--status denied|failed --note REASON`. Record actual fills with
   `--filled-qty Q --filled-price P` or `ticket.py fill`. Never record assumed
   fills. After a timeout or ambiguous response, reconcile broker orders before
   doing anything else; never blindly retry. A failed ticket needs a fresh
   risk check and a new ticket decision before retrying.
5. Before authorizing another order, sync broker state and rerun risk so daily
   limits include prior submissions. Never batch-authorize against stale state.

## Positions and the close

Register `alerts.py add --from-plan` and monitor positions. Bracket legs run
at the broker. Record stop/target fills. At `flat_by`, reconcile holdings,
run `ticket.py flatten --symbol SYMBOL --qty Q`, then `/trader-risk` and the
same authorization workflow. Cancel only that position's open bracket legs,
verify their status and remaining shares, then submit the closing ticket.
Use autonomous authorization for exits too. A scheduler/running agent is
required for monitoring and closing; this skill does not install one.

## What it never does

- Never submits without exact-order risk PASS and recorded authorization.
- Scheduled/background execution requires configured autonomy and authorized host tools.
- Never asks for, reads, stores or repeats API keys or passwords.
- Never switches `ALPACA_PAPER_TRADE` or `"paper"` to live. The user does that themselves.
- Never calls `close_all_positions`, `cancel_all_orders`, option or crypto order tools on its own.
- Never promises a fill price: a market order and a stop fill at whatever the market gives.

## Safety

- Education and tooling, not financial advice. A PASS is a rules check, not a recommendation.
- Paper trading by default (`"paper": true`). Going live is the user's own decision, in their own config.
- Only trader-broker submits orders, after trader-risk passes the exact order today.
  With `"autonomous": true` and Alpaca, execute via `ticket.py authorize` without
  per-order user confirmation, including scheduled/background runs. Otherwise use
  explicit per-order approval. Broker and host permissions must authorize execution.
- No options, margin, short selling or leverage unless the config allows it and the user confirms.
- Broker keys live in environment variables or the Claude Desktop config, never in the chat.
