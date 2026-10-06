# AI Day Trader

AI-assisted algorithmic trading platform built with a safety-first architecture.

## Initial goals

- Backtesting mode
- Paper-trading mode as the default
- Live-trading capability gated behind explicit configuration
- Alpaca brokerage integration
- Market scanner and strategy engine
- Deterministic risk engine and kill switch
- Portfolio, orders, positions, P&L, and analytics dashboard
- AI trade analysis and trade journal
- Mobile-friendly Safari/Chrome web interface

## Safety architecture

The AI analysis layer does not bypass the risk engine. Every executable order must pass deterministic risk checks including position sizing, daily-loss limits, exposure limits, stale-data checks, duplicate-order protection, and trading-mode validation.

Live trading is disabled by default. The initial development and validation workflow is:

`BACKTEST -> PAPER -> LIVE`

## Planned stack

- Python / FastAPI backend
- Alpaca Trading + Market Data APIs
- PostgreSQL-compatible persistence
- Responsive web frontend
- Render-ready deployment

> Automated trading involves substantial financial risk. Backtests and paper-trading results do not guarantee live performance.
