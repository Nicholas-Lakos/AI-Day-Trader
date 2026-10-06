from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass
class JournalEntry:
    symbol: str
    strategy: str
    side: str
    entry: float
    exit: float | None
    quantity: int
    stop: float
    target: float
    score: float
    rationale: str
    mode: str
    created_at: str

    @property
    def pnl(self) -> float | None:
        if self.exit is None:
            return None
        multiplier = 1 if self.side == "buy" else -1
        return round((self.exit - self.entry) * self.quantity * multiplier, 2)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["pnl"] = self.pnl
        return data


def new_entry(**kwargs) -> JournalEntry:
    return JournalEntry(created_at=datetime.now(timezone.utc).isoformat(), **kwargs)


def summarize(entries: list[JournalEntry]) -> dict:
    closed = [e for e in entries if e.pnl is not None]
    winners = [e for e in closed if e.pnl > 0]
    total_pnl = sum(e.pnl or 0 for e in closed)
    by_strategy: dict[str, dict] = {}
    for e in closed:
        stats = by_strategy.setdefault(e.strategy, {"trades": 0, "wins": 0, "pnl": 0.0})
        stats["trades"] += 1
        stats["wins"] += int((e.pnl or 0) > 0)
        stats["pnl"] = round(stats["pnl"] + (e.pnl or 0), 2)
    for stats in by_strategy.values():
        stats["win_rate_pct"] = round(stats["wins"] / stats["trades"] * 100, 2) if stats["trades"] else 0
    return {
        "closed_trades": len(closed),
        "win_rate_pct": round(len(winners) / len(closed) * 100, 2) if closed else 0,
        "total_pnl": round(total_pnl, 2),
        "by_strategy": by_strategy,
    }
