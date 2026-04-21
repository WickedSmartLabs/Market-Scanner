from scanner.queries.candles import get_recent_candles
from scanner.features.market_state import compute_trend_slope, compute_volatility
from scanner.features.regime import classify_trend, classify_volatility
from scanner.features.pause import detect_pause
from scanner.features.scoring import score_trend, score_pause, score_volatility
from scanner.features.atr import compute_atr
from scanner.features.volume import check_volume_confirmation
from scanner.features.candle_analysis import (
    compute_wick_ratio,
    compute_body_strength,
    compute_candles_confirming,
    compute_range_expansion,
    compute_vwap_relationship,
    score_options_fit,
)


def determine_status(score: int, pause_detected: bool) -> str:
    if pause_detected and score >= 6:
        return "This is important"
    if score >= 5:
        return "Getting interesting"
    return "Low priority"


def analyze_symbol(symbol: str, asset_class: str, timeframe: str, limit: int = 200) -> dict:
    candles = get_recent_candles(
        symbol=symbol,
        asset_class=asset_class,
        timeframe=timeframe,
        limit=limit,
    )

    if not candles:
        return _empty_analysis(symbol, asset_class, timeframe)

    opens = [c.open for c in candles]
    closes = [c.close for c in candles]
    highs = [c.high for c in candles]
    lows = [c.low for c in candles]
    volumes = [c.volume for c in candles]

    # Compute market state
    trend_slope = compute_trend_slope(closes, window=20)
    volatility = compute_volatility(closes, window=20)

    trend_regime = classify_trend(trend_slope)
    volatility_regime = classify_volatility(volatility, low_thresh=0.0008, high_thresh=0.0025)

    # Detect pause
    pause_detected, distance_series = detect_pause(closes, trend_regime, ma_window=20, lookback=5)

    # Compute ATR
    atr = compute_atr(highs, lows, closes, period=14)

    # Volume confirmation
    volume_confirmed = check_volume_confirmation(volumes, lookback=20)

    # Candle structure features
    wick_ratios = compute_wick_ratio(highs, lows, opens, closes, lookback=5)
    body_strength = compute_body_strength(highs, lows, opens, closes, atr, lookback=5)
    candles_confirming = compute_candles_confirming(closes, trend_regime, lookback=5)
    range_expansion = compute_range_expansion(highs, lows, atr, lookback=5)
    vwap_relationship = compute_vwap_relationship(closes, highs, lows, volumes, lookback=20)
    options_fit = score_options_fit(
        body_strength=body_strength,
        range_expansion=range_expansion,
        candles_confirming_label=candles_confirming.get("label"),
        volatility_regime=volatility_regime,
        structure_state="continuation" if pause_detected else "unknown",
    )

    # Score setup quality
    base_score = (
        score_trend(trend_slope)
        + score_pause(pause_detected, distance_series)
        + score_volatility(volatility_regime)
    )

    total_score = base_score + (1 if pause_detected and volume_confirmed else 0)
    total_score = min(total_score, 10)

    status = determine_status(total_score, pause_detected)

    latest_close = closes[-1] if closes else None
    latest_volume = volumes[-1] if volumes else None
    reference_stop = (atr * 1.5) if atr and latest_close else None

    analysis = {
        "summary": {
            "symbol": symbol,
            "asset_class": asset_class,
            "timeframe": timeframe,
            "direction": (
                "Up" if trend_regime == "uptrend"
                else "Down" if trend_regime == "downtrend"
                else "Sideways"
            ),
            "market_activity": (
                "Quiet" if volatility_regime == "low"
                else "Active" if volatility_regime == "high"
                else "Normal"
            ),
            "setup": "Trend continuation after a pause" if pause_detected else "None",
            "confidence": int(total_score),
            "status": status,
        },
        "details": {
            "candles_loaded":          len(closes),
            "trend_slope":             trend_slope,
            "volatility":              volatility,
            "trend_regime":            trend_regime,
            "volatility_regime":       volatility_regime,
            "pause_detected":          pause_detected,
            "distance_from_trend":     distance_series,
            "volume_confirmed":        volume_confirmed,
            "atr":                     atr,
            "latest_close":            latest_close,
            "latest_volume":           latest_volume,
            "reference_stop_distance": reference_stop,
            "upper_wick_ratio":        wick_ratios["upper_wick_ratio"],
            "lower_wick_ratio":        wick_ratios["lower_wick_ratio"],
            "body_strength":           body_strength,
            "candles_confirming":      candles_confirming,
            "range_expansion":         range_expansion,
            "vwap_relationship":       vwap_relationship,
            "options_fit":             options_fit,
        },
    }

    return analysis


def _empty_analysis(symbol: str, asset_class: str, timeframe: str) -> dict:
    return {
        "summary": {
            "symbol":          symbol,
            "asset_class":     asset_class,
            "timeframe":       timeframe,
            "direction":       "Unknown",
            "market_activity": "Unknown",
            "setup":           "None",
            "confidence":      0,
            "status":          "Low priority",
        },
        "details": {
            "candles_loaded":          0,
            "trend_slope":             None,
            "volatility":              None,
            "trend_regime":            "unknown",
            "volatility_regime":       "unknown",
            "pause_detected":          False,
            "distance_from_trend":     [],
            "volume_confirmed":        False,
            "atr":                     None,
            "latest_close":            None,
            "latest_volume":           None,
            "reference_stop_distance": None,
            "upper_wick_ratio":        None,
            "lower_wick_ratio":        None,
            "body_strength":           None,
            "candles_confirming":      {"count": None, "label": "unknown"},
            "range_expansion":         "unknown",
            "vwap_relationship":       "unknown",
            "options_fit":             "unknown",
        },
    }
