from datetime import timedelta

from scanner.storage.db import SessionLocal
from scanner.storage.models import Candle
from scanner.storage.analysis_models import AnalysisRun


LOOKAHEAD = {
    "crypto": {"1m": 15},
    "stock": {"1d": 5},
}


def evaluate_outcomes():
    session = SessionLocal()

    runs = (
        session.query(AnalysisRun)
        .filter(AnalysisRun.outcome_evaluated == False)
        .all()
    )

    for run in runs:
        lookahead = LOOKAHEAD.get(run.asset_class, {}).get(run.timeframe)
        if not lookahead:
            continue

        start_time = run.created_at
        end_time = start_time + timedelta(
            minutes=lookahead if run.timeframe == "1m" else lookahead * 1440
        )

        candles = (
            session.query(Candle)
            .filter(
                Candle.symbol == run.symbol,
                Candle.timeframe == run.timeframe,
                Candle.timestamp > start_time,
                Candle.timestamp <= end_time,
            )
            .order_by(Candle.timestamp.asc())
            .all()
        )

        # Not enough future data yet
        if len(candles) < lookahead:
            continue

        signal_price = candles[0].close
        prices = [c.close for c in candles]

        max_price = max(prices)
        min_price = min(prices)

        max_favorable = (
            (max_price - signal_price) / signal_price
            if run.summary["direction"] == "Up"
            else (signal_price - min_price) / signal_price
        )

        max_adverse = (
            (signal_price - min_price) / signal_price
            if run.summary["direction"] == "Up"
            else (max_price - signal_price) / signal_price
        )

        net_move = (prices[-1] - signal_price) / signal_price

        direction_correct = (
            (net_move > 0 and run.summary["direction"] == "Up")
            or (net_move < 0 and run.summary["direction"] == "Down")
        )

        run.outcome = {
            "signal_price": round(signal_price, 4),
            "lookahead_candles": len(candles),
            "max_favorable_pct": round(max_favorable * 100, 2),
            "max_adverse_pct": round(max_adverse * 100, 2),
            "net_move_pct": round(net_move * 100, 2),
            "direction_correct": direction_correct,
        }

        run.outcome_evaluated = True
        session.add(run)

    session.commit()
    session.close()
