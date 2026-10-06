from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    trading_mode: Literal["backtest", "paper", "live"] = "paper"
    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""
    database_url: str = "sqlite:///./trader.db"

    max_risk_per_trade_pct: float = Field(default=0.50, gt=0, le=5)
    max_position_pct: float = Field(default=10.0, gt=0, le=100)
    max_daily_loss_pct: float = Field(default=2.0, gt=0, le=25)
    max_open_positions: int = Field(default=5, gt=0, le=100)
    live_trading_enabled: bool = False

    @property
    def execution_allowed(self) -> bool:
        if self.trading_mode == "live":
            return self.live_trading_enabled
        return self.trading_mode == "paper"


settings = Settings()
