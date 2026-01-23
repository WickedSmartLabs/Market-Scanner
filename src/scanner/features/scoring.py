def score_trend(slope):
    if slope is None:
        return 0
    strength = abs(slope)
    if strength > 1.0:
        return 3
    if strength > 0.3:
        return 2
    if strength > 0.1:
        return 1
    return 0

def score_pause(pause_detected, distance_series):
    if not pause_detected or not distance_series:
        return 0

    improvement = abs(distance_series[0]) - abs(distance_series[-1])

    if improvement > 0.5:
        return 4
    if improvement > 0.2:
        return 3
    if improvement > 0.05:
        return 2
    return 1

def score_volatility(vol_regime):
    if vol_regime == "low":
        return 3
    if vol_regime == "normal":
        return 2
    return 0
