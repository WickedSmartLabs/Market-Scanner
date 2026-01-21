from scanner.queries.candles import get_recent_candles
from scanner.features.market_state import (
    compute_trend_slope,
    compute_volatility,
)
from scanner.features.regime import (
    classify_trend,
    classify_volatility,
)
from scanner.features.pause import detect_pause
from scanner.features.scoring import (
    score_trend,
    score_pause,
    score_volatility,
)
from scanner.presentation.formatter import format_analysis


def determine_status(score: int, pause_detected: bool) -> str:
    """
    Status reflects attention level only.
    """
    if pause_detected and score >= 6:
        return "This is important"
    if score >= 5:
        return "Getting interesting"
    return "Low priority"


if __name__ == "__main__":
    # --- Load recent market data (canonical example) ---
    candles = get_recent_candles(
        symbol="BTC/USD",
        asset_class="crypto",
        timeframe="1m",
        limit=120,
    )

    closes = [c.close for c in candles]

    # --- Compute basic market state ---
    trend_slope = compute_trend_slope(closes, window=20)
    volatility = compute_volatility(closes, window=20)

    trend_regime = classify_trend(trend_slope)
    volatility_regime = classify_volatility(
        volatility,
        low_thresh=0.0008,
        high_thresh=0.0025,
    )

    # --- Detect pause against the trend ---
    pause_detected, distance_series = detect_pause(
        closes,
        trend_regime,
        ma_window=20,
        lookback=5,
    )

    # --- Score overall setup quality ---
    total_score = (
        score_trend(trend_slope)
        + score_pause(pause_detected, distance_series)
        + score_volatility(volatility_regime)
    )

    # --- Determine attention status ---
    status = determine_status(total_score, pause_detected)

    # --- Build analysis result ---
    analysis = {
        "summary": {
            "symbol": "BTC/USD",
            "timeframe": "1m",
            "direction": (
                "Down" if trend_regime == "downtrend"
                else "Up" if trend_regime == "uptrend"
                else "Sideways"
            ),
            "market_activity": (
                "Quiet" if volatility_regime == "low"
                else "Active" if volatility_regime == "high"
                else "Normal"
            ),
            "setup": (
                "Trend continuation after a pause"
                if pause_detected
                else "None"
            ),
            "confidence": total_score,
            "status": status,
        },
        "details": {
            "candles_loaded": len(closes),
            "trend_slope": trend_slope,
            "volatility": volatility,
            "trend_regime": trend_regime,
            "volatility_regime": volatility_regime,
            "pause_detected": pause_detected,
            "distance_from_trend": distance_series,
            "notes": [
                (
                    "Pullback stalled against the trend"
                    if pause_detected
                    else "No pause detected"
                ),
                (
                    "Volatility remained contained"
                    if volatility_regime != "high"
                    else "Volatility expanding"
                ),
            ],
        },
    }

    # --- Output ---
    print(format_analysis(analysis))
