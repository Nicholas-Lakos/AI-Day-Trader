from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from app.config import settings


class Broker:
    def __init__(self) -> None:
        self._client = None

    def _get_client(self) -> TradingClient:
        if not settings.alpaca_api_key or not settings.alpaca_secret_key:
            raise RuntimeError("Alpaca credentials are not configured")
        if settings.trading_mode == "backtest":
            raise RuntimeError("Broker execution is disabled in backtest mode")
        if settings.trading_mode == "live" and not settings.live_trading_enabled:
            raise RuntimeError("Live trading is locked")

        paper = settings.trading_mode != "live"
        if self._client is None:
            self._client = TradingClient(
                settings.alpaca_api_key,
                settings.alpaca_secret_key,
                paper=paper,
            )
        return self._client

    def account(self):
        return self._get_client().get_account()

    def positions(self):
        return self._get_client().get_all_positions()

    def submit_market_order(self, symbol: str, qty: int, side: str):
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        order = MarketOrderRequest(
            symbol=symbol.upper(),
            qty=qty,
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        return self._get_client().submit_order(order_data=order)

    def kill_switch(self):
        client = self._get_client()
        client.cancel_orders()
        return client.close_all_positions(cancel_orders=True)


broker = Broker()
