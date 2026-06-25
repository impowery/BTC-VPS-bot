# Контекст для работы с торговыми ботами

## Что за продукт

5 торговых ботов на Python для DEX perps (Hyperliquid + Paradex testnet + Lighter код готов).
Каждый бот: $50 cash, 3x leverage, $150 buying power.
Боты работают 24/7 на VPS 193.233.19.171 (root) в screen-сессциях.
Дашборд: http://193.233.19.171:8080/report_latest.html (обновление 5 мин через cron)

## Структура файлов на сервере

```
/root/
  btc_bot.py            BTC v9  (STATE_FILE = /root/bots/btc_bot_state_v9.json)
  hype_bot.py           HYPE v8.1  (STATE_FILE = /root/bots/hype_bot_state_v8.1.json)
  gold_bot.py           GOLD v10.2  (STATE_FILE = /root/bots/gold_bot_state_v10.2.json)
  wti_bot.py            WTI v9  (STATE_FILE = /root/bots/wti_bot_state_v7.json)
  xyz100_bot.py         XYZ100 v7  (STATE_FILE = /root/bots/xyz100_bot_state_v7.json)  ← ВАЖНО: v7, не v7.1
  start_bots.sh         оригинальный запускатор
  start_bots_v2.sh      запускатор с wrapper + логами
  paradex_venv/         venv для Paradex
  bots/
    paradex_btc_bot.py          Paradex testnet бот (STATE_FILE = paradex_btc_bot_state.json)
    trades_*.jsonl              trade logs
    *_state_*.json              state файлы (множество версий, активные см. выше)
    gen_report.py               генератор дашборда (см. ниже "Дашборд фичи")
    report_latest.html          дашборд (~165KB, 6 ботов, sticky nav + color-coded buttons)
    reports/                    архив отчётов (report_<timestamp>.html)
    logs/                       логи всех ботов
    health_check.py             health check (cron 30 мин)
    bot_wrapper.py              auto-restart wrapper
    verify_deployment.py        post-deploy проверка
    paradex_testnet_account.json Paradex testnet ключи
    lighter_testnet_account.json Lighter testnet кошелёк (0.06 Sepolia ETH, не пригодился)
    _fix_scripts/               патч-скрипты
    gen_report.py.bak_<ts>      бэкапы перед изменениями
```

## Версии ботов

| Бот | Версия | State файл (АКТИВНЫЙ) | Что менялось |
|---|---|---|---|
| BTC | v7→v8→**v9** | btc_bot_state_v9.json | v8: ATR 2.0, TP 1.5/3.0, MAX_LOSS $25, ADX≥20, RSI 80/22. v9: ATR 1.5, TP 1.0/2.0, MAX_LOSS $15, ADX≥15, RSI 85/18 |
| HYPE | v7→**v8.1** | hype_bot_state_v8.1.json | EMA_X acceleration (1-entry: 2-candle, 2-entry: 1-candle, 3-entry: immediate) + MAX_LOSS $8 |
| WTI | **v9** | wti_bot_state_v7.json | оригинал, не трогал |
| GOLD | **v10.2** | gold_bot_state_v10.2.json | оригинал, не трогал |
| XYZ100 | v7.1→**v7** | xyz100_bot_state_v7.json | v7.1 (ужесточённые фильтры) заблокировал все сделки. Возвращаем v7. State файл переименован обратно в v7 |
| BTC-PARADEX | paradex-v1 | paradex_btc_bot_state.json | EMA crossover testnet, 0% maker / 0.02% taker |
| ETH | v7→v10 | — | **УДАЛИТЬ** — PF 0.10-0.38, не запущен, худший бот |

## Текущие метрики (report_latest, 25 Jun 10:25 MSK)

| Бот | PnL since reset | Trades | W/L | Вердикт |
|---|---:|---:|---:|---|
| WTI | +$101.93 | 87 | 48/39 | 🟢 лучший, оставить |
| BTC-PARADEX | +$68.24 | 7 | 2/1 | 🟡 testnet, ждать mainnet |
| GOLD | +$23.27 | 35 | 23/10 | 🟢 лучший win rate, оставить |
| XYZ100 | +$5.73 | 146 | 80/66 | 🟡 v7 восстановлен, растёт |
| BTC | +$3.81 | 119 | 48/71 | 🟡 v9 деплоен, ждём 5-7 дней |
| HYPE | +$1.16 | 547 | 269/161 | 🟡 восстанавливается после v8 фикса |

## Что сделано (фазы)

### Фаза 1: Фикс partial-close PnL bug
Баг: execute_tp1_close / execute_half_close обновляли balance, но НЕ писали в TRADE_LOG.
Фикс: tp1_realized_pnl accumulator. Backfill: BACKFILL_TP1 записи в каждый trade log.

### Фаза 2: BTC v8
ATR_MULT 1.2→2.0, TP1 0.8→1.5, TP2 1.5→3.0, MAX_LOSS=$25, ADX≥20, RSI 80/22.
Результат: PF 0.86 — слишком консервативный.

### Фаза 3: HYPE v8.1
EMA_X exit accelerated by position size. MAX_LOSS=$8.
Результат: 3-entry EMA_X max loss: -$8.36→-$0.15 (55x improvement). PF 8.18 (v8-only).

### Фаза 4: Paradex testnet
Paradex bot запущен, в дашборде. 0% maker / 0.02% taker.
Lighter бот код готов, но testnet требует собственный L1 (не Sepolia). Ждать mainnet.

### Фаза 5: Safety measures (3 слоя)
1. health_check.py (cron 30 мин): проверка screen, state freshness, crash tracebacks
2. bot_wrapper.py: auto-restart через 10 сек при краше
3. Логи в файл /root/bots/logs/{name}_bot.log
4. BTC assertions: MAX_LOSS, ADX_THRESHOLD, RSI_PERIOD проверяются при старте
5. verify_deployment.py: post-deploy проверка

### Фаза 6: Atomic save_state (КРИТИЧНЫЙ ФИКС)
Проблема: при краше во время save_state() файл обрезался → бот терял открытую позицию.
Фикс (все 5 HL ботов):
- save_state: shutil.copy2(.bak) → write .tmp → os.replace (атомарно)
- load_state: логирует CRITICAL при битом state, пытается восстановить из .bak
- import os добавлен всем ботам
- health_check: НЕ рестартит при битом state (бесполезно), пишет alert

### Фаза 7: BTC v9 (middle ground)
v8 был слишком консервативный (PF 0.86). v9: ATR 1.5, TP1 1.0x, TP2 2.0x, MAX_LOSS $15, ADX≥15, RSI 85/18.

### Фаза 8: XYZ100 откат к v7
v7.1 (ATR 0.8%, EMA 0.3%, ADX≥30) блокировал 100% входов. Возвращён v7 (state файл v7.json).

### Фаза 9: Дашборд UX (25 Jun 2026)
1. **Sticky-навигация по активам** — кнопки GOLD | BTC | HYPE | XYZ100 | WTI | BTC-PARADEX | ↑ Top в шапке, всегда видны при скролле. Клик перекидывает к карточке актива (якоря `#asset-NAME`).
2. **Цвет кнопок по последней сделке** — зелёная = последняя сделка прибыль, красная = убыток, нейтральная = нет сделок.
3. **Active-state через IntersectionObserver** — при скролле активная секция подсвечивается красным glow (rootMargin `-80px 0px -70% 0px`).
4. **БАГ ФИКС:** gen_report.py читал устаревшие state-файлы:
   - BTC: читал `btc_bot_state_v8.json` ($0.00 balance), бот пишет в `v9.json` ($92.28)
   - XYZ100: читал `xyz100_bot_state_v7.1.json` ($150.00, не активен), бот пишет в `v7.json` ($155.73)
   - Оба пути исправлены в `BOTS` списке.
5. **scroll-margin-top: 60px** — sticky nav не перекрывает заголовок при прыжке.

## Безопасность (4 слоя)

```
Слой 1: assertions → бот не запустится без критических констант (MAX_LOSS/ADX/RSI)
Слой 2: bot_wrapper → краш = автоперезапуск через 10 сек
Слой 3: atomic save_state → state file никогда не битый + .bak recovery
Слой 4: health_check cron (30 мин) → проверка screen, state freshness, crash tracebacks
```

## Дашборд фичи (gen_report.py)

- **Sticky nav** с кнопками активов (`.asset-nav`, `position:sticky;top:0;z-index:100`)
- **Цвет nav-link** по последней сделки: `.pos` (зелёный glow), `.neg` (красный glow), нейтральный
- **`.active` state** через IntersectionObserver — подсветка текущей секции при скролле
- **Якоря** `id="asset-NAME"` на каждой карточке бота
- **Auto-refresh** через `<meta http-equiv="refresh" content="300">`
- **`#top`** для возврата наверх
- **Backup policy:** перед каждым изменением gen_report.py создаётся `gen_report.py.bak_<timestamp>`

## Доступ к серверу

```
ssh root@193.233.19.171
password: jhjsj%4#23
```

В моём окружении: `/home/z/.venv/bin/python3 /home/z/my-project/scripts/ssh_helper.py exec "command"`

## Команды

```bash
# Перезапустить всех ботов с wrapper
bash /root/bots/start_bots_v2.sh

# Проверить здоровье
/root/paradex_venv/bin/python3 /root/bots/verify_deployment.py

# Посмотреть лог
tail -50 /root/bots/logs/btc_bot.log

# Health check лог
cat /root/bots/health_check.log

# Перегенерировать дашборд вручную
cd /root/bots && python3 gen_report.py
```

## Cron

```
*/5 * * * * cd /root/bots && python3 gen_report.py
*/30 * * * * /root/paradex_venv/bin/python3 /root/bots/health_check.py >> /root/bots/health_check.log 2>&1
```

## Известные баги (НЕ починены)

- Stale-price TREND_CONFLICT в load_state (5 ботов) — может закрыть позицию при рестарте по несвежей цене
- Нет thread safety (нет Lock вокруг balance mutations)
- bot_wrapper иногда не запускается после health_check restart (нужно перезапускать через start_bots_v2.sh)
- Paradex testnet BBO пропал (нет ликвидности на testnet)

## Pending tasks (согласовано с пользователем)

1. **ETH** — удалить с сервера (PF 0.10-0.38, не запущен, худший бот)
2. Оценить BTC v9 (5-7 дней): если PF > 1.2 — стратегия починена
3. Оценить HYPE v8.1: PF должен восстановиться до 1.3+
4. WTI risk management: MaxDD > PnL, снизить daily loss limit

## Желательно (после основных задач)

- Починить stale-price TREND_CONFLICT в load_state
- Добавить threading.Lock
- Assertion-чек: |displayed_pnl - trade_sum_pnl| > $0.01 → alert
- Перейти на mainnet с $10-50 на бот

## Монетизация (research в /home/z/my-project/research/DEX_Bot_Monetization_Report.md, 724 строки)

1. BaaS + Builder Codes (0.1% per trade) — после 4-8 нед разработки
2. HL Vault (10% perf fee, non-custodial) — после 3+ мес track record
3. Course на Gumroad + referral codes — можно начать с $0

## Lighter

Код бота готов (`/home/z/my-project/scripts/lighter_btc_bot.py`), но Lighter testnet использует собственный L1 (не Sepolia). Sepolia ETH (0.06) на кошельке не пригодился. Ждать mainnet.

## LinkedIn

10 постов написаны, 3 графика на английском в `/home/z/my-project/download/` (fee comparison, before/after EMA_X, before/after bug). Контент-план: 2 поста/неделю.

## Файлы локально (/home/z/my-project/)

- `BOT_CONTEXT.md` — этот файл
- `upload/BOT_CONTEXT.md` — копия для аплоада
- `scripts/` — все патч-скрипты, ssh_helper, парсеры, анализаторы
  - `gen_report.py` — локальная копия для редактирования (заливается на сервер через base64)
  - `ssh_helper.py` — SSH wrapper
  - `check_xyz_balance.py`, `verify_balances.py` — диагностические скрипты
- `download/` — PDF аудит, Excel, CSV, LinkedIn графики, код ботов
- `research/` — DEX исследование, монетизация (724 строки)

## TL;DR для нового чата

«5 торговых ботов на DEX perps (Hyperliquid + Paradex testnet) на VPS 193.233.19.171. Боты: BTC v9, HYPE v8.1, GOLD v10.2, WTI v9, XYZ100 v7, BTC-PARADEX testnet. Лучшие: WTI +$101.93, GOLD +$23.27. Фиксы: partial-close PnL bug, EMA_X acceleration, atomic save_state, health-check cron. Дашборд http://193.233.19.171:8080/report_latest.html с sticky nav, color-coded кнопками (зелёная/красная по последней сделке) и IntersectionObserver. SSH: root@193.233.19.171 пароль jhjsj%4#23. Контекст: /home/z/my-project/BOT_CONTEXT.md»
