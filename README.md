# BTC cTrader Bot — Remote MCP (Linux VPS)

BTCUSD trend-following bot running on Linux VPS via cTrader Remote MCP.
No cTrader Desktop, no Windows needed — works 24/7.

## Strategy

- **EMA20 + ADX(14) Wilder + ATR(14)** on M5
- **Scale-in**: up to 3 entries × 0.1 lots = 0.3 BTC max
- **SL = 2×ATR** (tighter, cut losses faster)
- **TP1 = 1.5×ATR** (50% partial close)
- **TP2 = 4×ATR** (full close, RR = 2.0)
- **Trailing SL**: extreme_price - 2×ATR (only moves up)
- **Break-even**: when PnL ≥ 0.5%, SL = entry price
- **Time exit**: after 4h if |PnL| < 1%
- **Scale-in cooldown**: 5 min between entries

## Settings (BTCUSD specific)

| Parameter | Value | Notes |
|---|---|---|
| SYMBOL_NAME | BTCUSD | cTrader demo |
| SYMBOL_ID | 22395 | Found via get_symbols |
| LOT_SIZE | 1 | 1 lot = 1 BTC |
| PIP_DIGITS | 5 | $59,250.50 = 5,925,050,000 pipettes |
| ENTRY_VOLUMES | 0.1, 0.1, 0.1 | 0.3 BTC max |
| SL_ATR_MULT | 2.0 | ATR-based |
| TP2_ATR_MULT | 4.0 | RR = 2.0 |

## PnL projection (at ATR=$120)

- **SL**: -$240 move = -$24 on 0.1 lot
- **TP2**: +$480 move = +$48 on 0.1 lot
- **Margin**: 0.3 BTC × $59,000 / 10 = $1,770 (36% of $5K)
- **EV/trade** (WR 60%): +$19.2

## Setup

1. Clone repo on VPS:
   ```bash
   git clone https://github.com/impowery/BTC-VPS-bot.git
   cd BTC-VPS-bot/gold_ctrader_bot
   ```

2. Install deps:
   ```bash
   pip install httpx python-dotenv numpy
   ```

3. Create `.env` (see config.py for template):
   ```
   MCP_URL=https://mcp.ctrader.com/trading/mcp
   MCP_BEARER_TOKEN=<your Remote MCP token>
   SYMBOL_NAME=BTCUSD
   SYMBOL_ID=22395
   LOT_SIZE=1
   PIP_DIGITS=5
   ENTRY_VOLUMES=0.1,0.1,0.1
   DRY_RUN=false
   ```

4. Get Remote MCP token:
   - Go to ctrader.com → Sign in
   - Open demo account
   - Settings → Remote MCP → Generate token

5. Run in screen:
   ```bash
   screen -dmS btc-remote bash -c 'cd /root/BTC-VPS-bot/gold_ctrader_bot && python3 -u gold_mcp_bot_remote.py 2>&1 | tee /root/bots/logs/btc_remote.log'
   ```

## Files

| File | Purpose |
|---|---|
| `gold_mcp_bot_remote.py` | Main bot (Remote MCP client + strategy + VPS sync) |
| `strategy.py` | EMA + ADX (Wilder) + ATR signal generation |
| `settings.py` | Strategy constants (imported by strategy.py) |
| `config.py` | .env template |
| `backfill_trades.py` | Fetch deals from cTrader → trades_btc_ctrader.jsonl |
| `.gitignore` | Excludes .env, state files, trade logs |

## VPS sync

Bot pushes to VPS HTTP server (ctrader_trades_server.py on :8089):
- POST /api/state — every 60 sec (with `symbol_name: BTCUSD` for routing)
- POST /api/trade — on each closed trade

Dashboard: http://193.233.19.171:8080/report_latest.html
Shows as "BTC-CTRADER" in bot list.

## Remote MCP API

Bot uses 16 cTrader Remote MCP tools:
- `get_balance`, `get_positions`, `get_symbols`, `get_trendbars`
- `create_order` (with relativeStopLoss/relativeTakeProfit)
- `amend_position` (SL/TP as display prices)
- `close_position` (full or partial)

Volume conversion: `lots × LOT_SIZE × 100 = cents`
- 0.1 lots × 1 × 100 = 10 cents (0.1 BTC)

Price conversion: `pipettes / 10^PIP_DIGITS = display price`
- 5,925,050,000 / 100,000 = $59,250.50
