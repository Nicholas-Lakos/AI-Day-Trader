from dataclasses import asdict

import pandas as pd

from app.strategies import evaluate_symbol


def rank_market(universe: dict[str, pd.DataFrame], limit: int = 20) -> list[dict]:
    ranked = []
    for symbol, bars in universe.items():
        signals = evaluate_symbol(symbol, bars)
        actionable = [s for s in signals if s.side != "hold"]
        best = max(actionable or signals, key=lambda s: s.score)
        ranked.append(asdict(best))
    ranked.sort(key=lambda item: (item["side"] != "hold", item["score"]), reverse=True)
    return ranked[:limit]
