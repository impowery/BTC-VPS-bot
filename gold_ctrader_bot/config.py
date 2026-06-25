# BTC cTrader Bot — config
# Copy to .env and fill in your real values

# === MCP (Remote cTrader Web) ===
MCP_URL=https://mcp.ctrader.com/trading/mcp
MCP_BEARER_TOKEN=<your_remote_mcp_token>

# === Strategy (BTCUSD trend-following) ===
SYMBOL_NAME=BTCUSD
SYMBOL_ID=22395
LOT_SIZE=1
PIP_DIGITS=5
MONEY_DIGITS=2
MIN_INTERVAL_MINUTES=30
MAX_LOSS_PERCENT=2.5

# Scale-in (lots per entry) — 0.1 BTC each, 0.3 max
ENTRY_VOLUMES=0.1,0.1,0.1
MAX_ENTRIES=3
SL_ATR_MULT=2.0
TP1_ATR_MULT=1.5
TP2_ATR_MULT=4.0
TRAIL_ACTIVATE_PCT=0.5
TIME_EXIT_HOURS=4
BE_TRIGGER_PCT=0.5
BE_OFFSET_ATR=0.0

TIMEFRAME=M_5
CANDLE_COUNT=100
CHECK_INTERVAL=60

RECONNECT_DELAY=5
MAX_RECONNECT_DELAY=300

# === VPS sync (push to HTTP server on VPS) ===
VPS_SYNC_ENABLED=true
VPS_SYNC_URL=http://127.0.0.1:8089
VPS_AUTH_TOKEN=gold2026secret
TRADE_LOG_PATH=/root/bots/trades_btc_ctrader.jsonl
STATE_FILE_PATH=state_btc_remote.json
DRY_RUN=false
