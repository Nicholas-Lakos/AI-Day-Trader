from dataclasses import dataclass

from app.config import settings


@dataclass
class TradeProposal:
    symbol: str
    side: str
    entry_price: float
    stop_price: float
    account_equity: float
    current_daily_pnl: float
    open_positions: int


@dataclass
class RiskDecision:
    approved: bool
    reason: str
    quantity: int = 0
    dollars_at_risk: float = 0.0


def evaluate_trade(p: TradeProposal) -> RiskDecision:
    if p.account_equity <= 0:
        return RiskDecision(False, "Account equity must be positive")
    if p.entry_price <= 0 or p.stop_price <= 0:
        return RiskDecision(False, "Prices must be positive")
    if p.side not in {"buy", "sell"}:
        return RiskDecision(False, "Unsupported side")
    if p.open_positions >= settings.max_open_positions:
        return RiskDecision(False, "Maximum open positions reached")

    daily_loss_limit = p.account_equity * settings.max_daily_loss_pct / 100
    if p.current_daily_pnl <= -daily_loss_limit:
        return RiskDecision(False, "Daily loss kill switch is active")

    risk_per_share = abs(p.entry_price - p.stop_price)
    if risk_per_share <= 0:
        return RiskDecision(False, "Stop price must differ from entry")

    risk_budget = p.account_equity * settings.max_risk_per_trade_pct / 100
    position_cap = p.account_equity * settings.max_position_pct / 100
    qty_by_risk = int(risk_budget // risk_per_share)
    qty_by_cap = int(position_cap // p.entry_price)
    quantity = min(qty_by_risk, qty_by_cap)

    if quantity < 1:
        return RiskDecision(False, "Trade is too large for configured risk limits")

    return RiskDecision(
        True,
        "Approved by deterministic risk controls",
        quantity=quantity,
        dollars_at_risk=round(quantity * risk_per_share, 2),
    )
