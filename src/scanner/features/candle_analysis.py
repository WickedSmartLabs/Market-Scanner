import numpy as np


def compute_wick_ratio(highs, lows, opens, closes, lookback=5):
    """
    Average wick ratio over recent candles.
    Returns dict with upper_wick_ratio and lower_wick_ratio (0.0-1.0).
    High ratio = lots of rejection, low ratio = strong directional bodies.
    """
    if len(closes) < lookback:
        return {"upper_wick_ratio": None, "lower_wick_ratio": None}

    highs = np.array(highs[-lookback:], dtype=float)
    lows = np.array(lows[-lookback:], dtype=float)
    opens = np.array(opens[-lookback:], dtype=float)
    closes = np.array(closes[-lookback:], dtype=float)

    total_range = highs - lows
    total_range = np.where(total_range == 0, 1e-10, total_range)

    upper_wicks = highs - np.maximum(opens, closes)
    lower_wicks = np.minimum(opens, closes) - lows

    upper_ratio = float(np.mean(upper_wicks / total_range))
    lower_ratio = float(np.mean(lower_wicks / total_range))

    return {
        "upper_wick_ratio": round(upper_ratio, 3),
        "lower_wick_ratio": round(lower_ratio, 3),
    }


def compute_body_strength(highs, lows, opens, closes, atr, lookback=5):
    """
    Average candle body size relative to ATR.
    > 0.6 = strong momentum candles
    0.3-0.6 = moderate
    < 0.3 = weak/indecision
    """
    if len(closes) < lookback or not atr:
        return None

    opens = np.array(opens[-lookback:], dtype=float)
    closes = np.array(closes[-lookback:], dtype=float)

    bodies = np.abs(closes - opens)
    avg_body = float(np.mean(bodies))

    return round(avg_body / atr, 3)


def compute_candles_confirming(closes, trend_regime, lookback=5):
    """
    Count how many of the last N candles confirm the trend direction.
    Returns int 0-lookback and a label.
    """
    if len(closes) < lookback + 1 or trend_regime == "unknown":
        return {"count": None, "label": "unknown"}

    recent = closes[-lookback:]
    confirming = 0

    for i in range(1, len(recent)):
        if trend_regime == "uptrend" and recent[i] > recent[i - 1]:
            confirming += 1
        elif trend_regime == "downtrend" and recent[i] < recent[i - 1]:
            confirming += 1

    ratio = confirming / (lookback - 1)

    if ratio >= 0.8:
        label = "strong_confirmation"
    elif ratio >= 0.5:
        label = "moderate_confirmation"
    else:
        label = "weak_confirmation"

    return {"count": confirming, "label": label}


def compute_range_expansion(highs, lows, atr, lookback=5):
    """
    Whether recent candle ranges are expanding or contracting vs ATR baseline.
    Expanding = momentum building, contracting = compression/exhaustion.
    """
    if len(highs) < lookback or not atr:
        return "unknown"

    highs = np.array(highs[-lookback:], dtype=float)
    lows = np.array(lows[-lookback:], dtype=float)

    recent_ranges = highs - lows
    avg_recent_range = float(np.mean(recent_ranges))

    ratio = avg_recent_range / atr

    if ratio > 1.2:
        return "expanding"
    if ratio < 0.7:
        return "contracting"
    return "normal"


def compute_vwap_relationship(closes, highs, lows, volumes, lookback=20):
    """
    Whether latest price is above, below, or at VWAP.
    Uses a rolling VWAP over the lookback window.
    """
    if len(closes) < lookback:
        return "unknown"

    closes = np.array(closes[-lookback:], dtype=float)
    highs = np.array(highs[-lookback:], dtype=float)
    lows = np.array(lows[-lookback:], dtype=float)
    volumes = np.array(volumes[-lookback:], dtype=float)

    typical_price = (highs + lows + closes) / 3
    total_volume = np.sum(volumes)

    if total_volume == 0:
        return "unknown"

    vwap = float(np.sum(typical_price * volumes) / total_volume)
    latest_close = float(closes[-1])

    diff_pct = (latest_close - vwap) / vwap

    if diff_pct > 0.002:
        return "above"
    if diff_pct < -0.002:
        return "below"
    return "at"


def score_options_fit(body_strength, range_expansion, candles_confirming_label,
                      volatility_regime, structure_state):
    """
    Rule-based options fit score.
    Returns: good / mediocre / poor
    """
    # Poor conditions
    if range_expansion == "contracting":
        return "poor"
    if body_strength is not None and body_strength < 0.25:
        return "poor"
    if candles_confirming_label in ("weak_confirmation",):
        return "poor"
    if volatility_regime == "high" and structure_state != "continuation":
        return "poor"

    # Good conditions
    if (
        range_expansion == "expanding"
        and body_strength is not None and body_strength > 0.5
        and candles_confirming_label == "strong_confirmation"
    ):
        return "good"

    return "mediocre"
