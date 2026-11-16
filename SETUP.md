# Set up autonomous paper trading

## Give this to your agent

> Update my installed day-trader skill from
> https://github.com/PrimeDeep1/day-trader-skill. Back up the installation first.
> Preserve .env, credentials, trader/config.json, portfolio, research and state.
> Load the root SKILL.md and bundled trader-*/SKILL.md files from this version;
> locate and disable any duplicate older day-trading skill with my authorization.
> From the project working folder run the repository's configure.py by absolute
> path. This enables autonomy without changing existing paper/live or risk settings.
> I authorize autonomous paper trading and the supported host permission setup
> for Alpaca stock orders and individual bracket-leg cancellation. Keep paper:true;
> if my existing config is live, stop before enabling broker writes and report it.
> Follow SETUP.md to expose the broker tools, reload the MCP server and start a
> fresh chat. Verify the account and effective permissions. Do not place an
> arbitrary test trade. Once ready, follow the configured strategy and risk limits
> autonomously without asking for a fresh yes for every entry or exit.

## Local setup

Requires Python 3.8+; the bundled tools use the standard library.

```bash
git clone https://github.com/PrimeDeep1/day-trader-skill.git
cd day-trader-skill
python3 configure.py
```

If your `trader/` data lives elsewhere, run the script by absolute path from that
project folder, or pass `--config /absolute/project/trader/config.json`.
The helper creates a paper config for a new project. For an existing config,
it backs up the original and sets only `autonomous` to true. It does not modify
.env, credentials, portfolio, state, broker selection, risk limits or paper/live.
To deliberately choose manual confirmation: `python3 configure.py --manual`.

Review the initial $5,000 budget and risk defaults for a new project before use.
The helper never starts a trading loop or submits an order.

## Connect an agent host

Install/load the repository root `SKILL.md` with your host's supported skill
loader, or install the eleven `trader-*` directories as individual skills.
Keep the scripts with their skills. `agent.json` is descriptive metadata, not a
host-specific plugin installer. Resolve script paths to the installation, but
run them with the working directory that contains your `trader/` data.

Use `trader-broker/mcp_config.example.json` as a generic MCP server example.
Map it to your host's supported schema; do not paste it over existing settings.
Store credentials locally in the host's secret environment. Never send them to
the AI or commit them. A .env file is not automatically loaded by these scripts;
configure your host/server to load its environment securely.

The Alpaca server needs `ALPACA_TOOLSETS=account,trading,stock-data` and
`ALPACA_PAPER_TRADE=true` for paper execution. The host must expose and authorize
`place_stock_order` and `cancel_order_by_id`, plus read tools for account,
positions, orders, clock and quotes. Discover actual tool names in your installed
server. Restrict cancellation to the strategy's individual bracket legs.

### Hermes Agent

Use `hermes mcp configure alpaca-paper` if your server is named `alpaca-paper`;
otherwise use its actual configured name. Inspect `hermes mcp --help` for the
installed version's supported configuration flow. Check both the server environment
and the `mcp_servers.<server>.tools.include` tool-selection setting. A server
limited to `account,stock-data` or an allowlist without order tools is read-only.
Configure unattended permission for the selected tools using Hermes's supported
settings; the repository cannot grant host permissions. Reload the MCP server.

Start a **new chat** after updating skills. If the agent still quotes an old
per-order yes rule, ask it for the exact file path and loaded instruction source.
Update/disable stale user-installed copies through the supported loader. Do not
attempt to override higher-priority host policies with a prompt.

## Verify readiness

- The active config uses Alpaca, autonomy enabled, and the intended paper account.
- The agent loaded this version's root and broker skills in a new session.
- Broker read checks succeed and the two required write tools are exposed and
  authorized for unattended use. No arbitrary order is needed to check setup.
- A single active runner drives the strategy and monitors exits through flat_by.
- Run `python3 -m unittest discover -s tests -q` for offline regression checks.

Readiness checks are not proof of a broker fill. Confirm broker read-back when
a legitimate strategy order occurs. The pack does not implement a persistent
kill switch, atomic exposure reservations across runners, or broker idempotency.
Do not run concurrent trading agents on the same account. Keep the configured
risk limits and reconcile uncertain submissions before any further write.
