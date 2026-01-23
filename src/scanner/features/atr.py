import numpy as np


def compute_atr(highs, lows, closes, period=14):
    """
    Calculate Average True Range.
    Returns ATR value or None if insufficient data.
    """
    if len(highs) < period + 1:
        return None
    
    highs = np.array(highs, dtype=float)
    lows = np.array(lows, dtype=float)
    closes = np.array(closes, dtype=float)
    
    # True Range components
    h_l = highs[1:] - lows[1:]
    h_c = np.abs(highs[1:] - closes[:-1])
    l_c = np.abs(lows[1:] - closes[:-1])
    
    true_range = np.maximum(h_l, np.maximum(h_c, l_c))
    
    atr = np.mean(true_range[-period:])
    return float(atr)
