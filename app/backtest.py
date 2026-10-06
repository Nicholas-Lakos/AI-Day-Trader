from dataclasses import asdict, dataclass

import pandas as pd

from app.strategies import evaluate_symbol


@dataclass
class BacktestResult:
    symbol: str
    starting_equity: float
    ending_equity: float
    total_return_pct: float
    trades: int
    wins: int
    losses: int
    win_rate_pct: float
    max_drawdown_pct: float
    profit_factor: float | None


def run_backtest(symbol: str, bars: pd.DataFrame, starting_equity: float = 100_000.0,
                 risk_pct: float = 0.5) -> dict:
    equity = starting_equity
    peak = equity
    max_dd = 0.0
    wins = losses = 0
    gross_profit = gross_loss = 0.0
    trade_log = []

    for i in range(25, len(bars) - 1):
        history = bars.iloc[: i + 1]
        candidates = [s for s in evaluate_symbol(symbol, history) if s.side == "buy" and s.entry and s.stop and s.target]
        if not candidates:
            continue
        signal = max(candidates, key=lambda s: s.score)
        risk_per_share = signal.entry - signal.stop
        if risk_per_share <= 0:
            continue
        risk_budget = equity * risk_pct / 100
        qty = int(risk_budget // risk_per_share)
        if qty < 1:
            continue

        exit_price = None
        outcome = "timeout"
        for j in range(i + 1, min(i + 21, len(bars))):
            bar = bars.iloc[j]
            if float(bar.low) <= signal.stop:
                exit_price, outcome = signal.stop, "loss"
                break
            if float(bar.high) >= signal.target:
                exit_price, outcome = signal.target, "win"
                break
        if exit_price is None:
            exit_price = float(bars.iloc[min(i + 20, len(bars) - 1)].close)
            outcome = "win" if exit_price > signal.entry else "loss"

        pnl = (exit_price - signal.entry) * qty
        equity += pnl
        if pnl > 0:
            wins += 1
            gross_profit += pnl
        else:
            losses += 1
            gross_loss += abs(pnl)
        peak = max(peak, equity)
        max_dd = max(max_dd, (peak - equity) / peak * 100 if peak else 0)
        trade_log.append({"strategy": signal.strategy, "entry": signal.entry, "exit": exit_price,
                          "qty": qty, "pnl": round(pnl, 2), "outcome": outcome})

    trades = wins + losses
    result = BacktestResult(
        symbol=symbol,
        starting_equity=starting_equity,
        ending_equity=round(equity, 2),
        total_return_pct=round((equity / starting_equity - 1) * 100, 2),
        trades=trades,
        wins=wins,
        losses=losses,
        win_rate_pct=round(wins / trades * 100, 2) if trades else 0,
        max_drawdown_pct=round(max_dd, 2),
        profit_factor=round(gross_profit / gross_loss, 2) if gross_loss else None,
    )
    return {"summary": asdict(result), "trades": trade_log}
