import numpy as np

def compute_returns(closes):
    """
    Percentage returns between consecutive closes.
    """
    closes = np.array(closes, dtype=float)
    return np.diff(closes) / closes[:-1]

def compute_volatility(closes, window=20):
    """
    Realized volatility proxy: std dev of recent returns.
    """
    returns = compute_returns(closes)
    if len(returns) < window:
        return None
    return float(np.std(returns[-window:]))

def compute_trend_slope(closes, window=20):
    """
    Linear slope of price over a window.
    Positive = upward drift, negative = downward drift.
    """
    if len(closes) < window:
        return None

    y = np.array(closes[-window:], dtype=float)
    x = np.arange(len(y))
    slope = np.polyfit(x, y, 1)[0]
    return float(slope)
