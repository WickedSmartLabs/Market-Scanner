def classify_trend(slope, slope_threshold=0.0):
    """
    Classify trend direction based on slope.
    """
    if slope is None:
        return "unknown"
    if slope > slope_threshold:
        return "uptrend"
    if slope < -slope_threshold:
        return "downtrend"
    return "range"


def classify_volatility(volatility, low_thresh, high_thresh):
    """
    Classify volatility regime.
    """
    if volatility is None:
        return "unknown"
    if volatility < low_thresh:
        return "low"
    if volatility > high_thresh:
        return "high"
    return "normal"
