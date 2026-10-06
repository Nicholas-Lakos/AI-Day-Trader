from dataclasses import dataclass
from typing import Literal

import pandas as pd


@dataclass
class Signal:
    symbol: str
    strategy: str
    side: Literal["buy", "sell", "hold"]
    score: float
    entry: float | None = None
    stop: float | None = None
    target: float | None = None
    reason: str = ""


def _indicators(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    close = data["close"].astype(float)
    volume = data["volume"].astype(float)
    data["ema9"] = close.ewm(span=9, adjust=False).mean()
    data["ema20"] = close.ewm(span=20, adjust=False).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, float("nan"))
    data["rsi14"] = 100 - (100 / (1 + rs))
    data["avg_volume20"] = volume.rolling(20).mean()
    data["rel_volume"] = volume / data["avg_volume20"]
    typical = (data["high"] + data["low"] + data["close"]) / 3
    data["vwap"] = (typical * volume).cumsum() / volume.cumsum()
    data["range20_high"] = data["high"].shift(1).rolling(20).max()
    data["range20_low"] = data["low"].shift(1).rolling(20).min()
    return data


def evaluate_symbol(symbol: str, bars: pd.DataFrame) -> list[Signal]:
    if len(bars) < 25:
        return [Signal(symbol, "data_quality", "hold", 0, reason="Need at least 25 bars")]

    d = _indicators(bars).dropna()
    if d.empty:
        return [Signal(symbol, "data_quality", "hold", 0, reason="Indicators unavailable")]

    row = d.iloc[-1]
    price = float(row.close)
    vwap = float(row.vwap)
    ema9 = float(row.ema9)
    ema20 = float(row.ema20)
    rsi = float(row.rsi14)
    rv = float(row.rel_volume)
    high20 = float(row.range20_high)
    low20 = float(row.range20_low)
    signals: list[Signal] = []

    trend_score = sum([price > vwap, ema9 > ema20, rsi >= 52, rv >= 1.2]) / 4 * 100
    if trend_score >= 75:
        stop = min(vwap, ema20)
        risk = max(price - stop, price * 0.003)
        signals.append(Signal(symbol, "vwap_trend", "buy", trend_score, price, stop, price + 2 * risk,
                              "Price above VWAP with short-term trend and volume confirmation"))

    if price > high20 and rv >= 1.5:
        stop = max(high20 * 0.995, price * 0.985)
        risk = price - stop
        signals.append(Signal(symbol, "breakout", "buy", min(100, 70 + min(rv, 3) * 10), price, stop,
                              price + 2 * risk, "20-bar breakout confirmed by relative volume"))

    if rsi <= 30 and price < vwap:
        stop = min(low20, price * 0.985)
        risk = price - stop
        signals.append(Signal(symbol, "mean_reversion", "buy", min(90, 60 + (30 - rsi)), price, stop,
                              price + 1.5 * risk, "Oversold RSI below VWAP; mean-reversion candidate"))

    if not signals:
        signals.append(Signal(symbol, "combined", "hold", trend_score, reason="No strategy threshold met"))
    return signals
