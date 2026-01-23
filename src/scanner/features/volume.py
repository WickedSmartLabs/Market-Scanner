import numpy as np


def check_volume_confirmation(volumes, lookback=20, threshold=1.2):
    """
    Check if recent volume is above average.
    Returns True if recent 5-candle avg volume > threshold * lookback avg.
    """
    if len(volumes) < lookback + 5:
        return False
    
    volumes = np.array(volumes, dtype=float)
    avg_volume = np.mean(volumes[-lookback:])
    recent_volume = np.mean(volumes[-5:])
    
    return bool(recent_volume > avg_volume * threshold)
