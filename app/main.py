from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.broker import broker
from app.config import settings
from app.risk import TradeProposal, evaluate_trade

app = FastAPI(title="AI Day Trader", version="0.1.0")


class RiskCheckRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    side: str
    entry_price: float = Field(gt=0)
    stop_price: float = Field(gt=0)
    account_equity: float = Field(gt=0)
    current_daily_pnl: float = 0
    open_positions: int = Field(default=0, ge=0)


@app.get("/")
def root():
    return {
        "name": "AI Day Trader",
        "status": "online",
        "mode": settings.trading_mode,
        "live_trading_enabled": settings.live_trading_enabled,
    }


@app.get("/health")
def health():
    return {"ok": True, "mode": settings.trading_mode}


@app.post("/risk/check")
def risk_check(req: RiskCheckRequest):
    decision = evaluate_trade(TradeProposal(**req.model_dump()))
    return decision.__dict__


@app.get("/broker/account")
def broker_account():
    try:
        account = broker.account()
        return {
            "equity": str(account.equity),
            "cash": str(account.cash),
            "buying_power": str(account.buying_power),
            "status": str(account.status),
            "mode": settings.trading_mode,
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/broker/positions")
def broker_positions():
    try:
        return [
            {
                "symbol": p.symbol,
                "qty": str(p.qty),
                "market_value": str(p.market_value),
                "unrealized_pl": str(p.unrealized_pl),
            }
            for p in broker.positions()
        ]
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
