import numpy as np

def simple_moving_average(values, window):
    if len(values) < window:
        return None
    return np.convolve(values, np.ones(window)/window, mode="valid")

def detect_pause(closes, trend, ma_window=20, lookback=5):
    """
    Detects whether a pullback against the trend is stalling.
    Returns (pause_detected: bool, distance_series: list).
    """
    if len(closes) < ma_window + lookback:
        return False, []

    sma = simple_moving_average(closes, ma_window)
    recent_closes = closes[-len(sma):]

    # Distance from trend line
    distances = recent_closes - sma

    recent_distances = distances[-lookback:]

    if trend == "uptrend":
        # Pullback = price below MA, distance becoming less negative
        return (
            np.all(recent_distances < 0)
            and abs(recent_distances[-1]) < abs(recent_distances[0]),
            recent_distances.tolist(),
        )

    if trend == "downtrend":
        # Pullback = price above MA, distance becoming less positive
        return (
            np.all(recent_distances > 0)
            and abs(recent_distances[-1]) < abs(recent_distances[0]),
            recent_distances.tolist(),
        )

    return False, recent_distances.tolist()
